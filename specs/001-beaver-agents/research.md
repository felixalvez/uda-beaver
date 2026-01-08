# Research: Beaver's Choice Paper Company Multi-Agent System

**Phase**: 0 - Research & Discovery
**Date**: 2026-01-06
**Status**: Complete

## Executive Summary

All technical decisions for this project were pre-determined through the constitution document and user design decisions. This research document consolidates those decisions with their rationales and confirms best practices for implementation.

---

## Decision 1: Agent Framework Selection

**Decision**: smolagents (HuggingFace)

**Rationale**:
- Philosophy alignment: "The best agentic systems are the simplest" matches KISS principle
- `ManagedAgent` pattern directly supports Orchestrator → Specialist architecture
- `@tool` decorator provides clean, minimal tool definitions
- Best documentation quality for 6-hour implementation timeline
- Highly readable code for reviewer evaluation

**Alternatives Considered**:
| Framework | Pros | Cons | Verdict |
|-----------|------|------|---------|
| smolagents | Simple, well-documented, ManagedAgent pattern | Less mature than alternatives | SELECTED |
| pydantic-ai | Type-safe, structured outputs | More boilerplate, overkill for scope | REJECTED |
| npcpy | Lightweight | Less documentation, confusing terminology | REJECTED |

**Implementation Pattern**:
```python
from smolagents import tool, CodeAgent, ToolCallingAgent

# Tools use @tool decorator
@tool
def check_inventory(item_name: str) -> str:
    """Docstring becomes tool description."""
    return result

# Specialists use ToolCallingAgent
specialist = ToolCallingAgent(tools=[tool], model=model, name="name")

# Orchestrator uses CodeAgent with managed_agents
orchestrator = CodeAgent(tools=[], model=model, managed_agents=[specialists])
```

---

## Decision 2: Agent Architecture

**Decision**: 4-agent architecture (1 Orchestrator + 3 Specialists)

**Rationale**:
- Orchestrator handles routing and response compilation
- Each specialist has single responsibility (Inventory, Quote, Sales)
- Well under 5-agent maximum constraint
- Clear separation enables independent testing

**Agent Responsibilities**:

| Agent | Role | Tools |
|-------|------|-------|
| Orchestrator | Route inquiries, compile responses | None (delegates to managed agents) |
| Inventory Agent | Stock queries, autonomous reordering | check_inventory, get_all_inventory, trigger_reorder |
| Quote Agent | Pricing with bulk discounts | search_quote_history, get_item_price, calculate_quote |
| Sales Agent | Order fulfillment, delivery estimates | check_delivery_timeline, fulfill_order, get_cash_balance |

**Alternatives Considered**:
- 5 agents (add Financial Agent): Rejected - cash balance checks can live in Sales Agent
- 3 agents (merge Quote + Sales): Rejected - responsibilities are distinct enough to separate
- 2 agents (single specialist): Rejected - too much complexity in one agent

---

## Decision 3: Item Name Matching Strategy

**Decision**: LLM fuzzy matching via prompt engineering

**Rationale**:
- Customers use informal names ("A4 glossy paper") but database has exact names ("Glossy paper")
- LLM is already processing requests; matching is natural extension
- No additional tooling or fuzzy match library needed
- The inventory agent's system prompt will include the exact item names from `paper_supplies` list

**Implementation Approach**:
1. Include full product catalog in agent system prompt
2. Instruct agent to map customer terminology to exact database names
3. Agent returns normalized item names for tool calls

**Alternatives Considered**:
- Fuzzy string matching library (fuzzywuzzy): More complexity, additional dependency
- Lookup tool that returns closest matches: Adds round-trip, slows response
- Fail and ask for clarification: Poor user experience

---

## Decision 4: Inventory Reorder Trigger

**Decision**: Pre-fulfillment check

**Rationale**:
- Check stock before fulfilling orders
- If quantity would drop below `min_stock_level`, trigger reorder first
- Ensures stock is replenished proactively
- Prevents stockouts during active sales periods

**Implementation Logic**:
```
1. Customer orders X units of item
2. Check current_stock for item
3. If (current_stock - X) < min_stock_level:
   a. Calculate reorder quantity = min_stock_level + buffer
   b. Create stock_orders transaction
   c. Log reorder with estimated delivery date
4. Create sales transaction
5. Return confirmation with delivery estimate
```

**Alternatives Considered**:
- Daily proactive scan: Adds complexity, not triggered by actual demand
- On-demand only: Reactive, may cause stockouts

---

## Decision 5: Out-of-Stock Handling

**Decision**: Quote with supplier lead time

**Rationale**:
- 60% of products aren't initially stocked (40% coverage)
- Customers can still order; we order from supplier
- Delivery timeline based on quantity (0-7 days)
- Maintains sales opportunity rather than rejecting requests

**Delivery Timeline Formula** (from starter code):
| Quantity | Lead Time |
|----------|-----------|
| ≤10 units | Same day |
| 11-100 units | 1 day |
| 101-1000 units | 4 days |
| >1000 units | 7 days |

**Alternatives Considered**:
- Suggest alternatives only: Loses sales for specific product needs
- Decline order: Poor customer experience
- Partial fulfillment: Adds complexity, unclear customer expectation

---

## Decision 6: Bulk Discount Strategy

**Decision**: Tiered discounts with rounded totals

**Rationale**:
- Historical quotes show pattern of:
  - 10% discount on large orders
  - Rounding to "friendly" numbers ($50, $100, etc.)
  - Explanations justifying the discount
- Competitive pricing is an evaluation criterion

**Discount Tiers** (derived from historical quotes):
| Order Size | Discount |
|------------|----------|
| Small (<100 units) | 0-5% |
| Medium (100-500 units) | 5-10% |
| Large (>500 units) | 10-15% |

**Rounding Strategy**:
- Round total to nearest $5 for amounts <$100
- Round to nearest $10 for amounts $100-$500
- Round to nearest $50 for amounts >$500

---

## Decision 7: Database Integration

**Decision**: Reuse starter code SQLAlchemy engine and helper functions

**Rationale**:
- Starter code provides comprehensive helper functions
- SQLAlchemy engine already configured
- No need to rewrite database logic
- Follows DRY principle

**Helper Functions to Wrap**:
| Starter Function | Tool Wrapper |
|------------------|--------------|
| `get_stock_level(item, date)` | `check_inventory` |
| `get_all_inventory(date)` | `get_all_inventory` |
| `create_transaction(...)` | `fulfill_order`, `trigger_reorder` |
| `search_quote_history(terms)` | `search_quote_history` |
| `get_supplier_delivery_date(date, qty)` | `check_delivery_timeline` |
| `get_cash_balance(date)` | `get_cash_balance` |

---

## Decision 8: LLM Provider

**Decision**: User's own API key (OpenAI/Anthropic compatible)

**Rationale**:
- Development flexibility
- Not dependent on Udacity proxy availability
- Can use preferred model (GPT-4, Claude, etc.)

**Configuration**:
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
```

---

## Research Summary

| Area | Decision | Status |
|------|----------|--------|
| Framework | smolagents | CONFIRMED |
| Agent Count | 4 (Orchestrator + 3) | CONFIRMED |
| Item Matching | LLM fuzzy via prompt | CONFIRMED |
| Reorder Trigger | Pre-fulfillment check | CONFIRMED |
| Out-of-Stock | Quote with lead time | CONFIRMED |
| Bulk Discounts | Tiered with rounding | CONFIRMED |
| Database | Reuse starter helpers | CONFIRMED |
| LLM Provider | User's API key | CONFIRMED |

**All technical decisions resolved. Ready for Phase 1: Design & Contracts.**
