# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-agent system for Beaver's Choice Paper Company handling:
- Inventory management and reordering
- Quote generation with pricing strategies
- Sales transaction fulfillment

**Constraint**: Maximum 5 agents. Text-based inputs/outputs only.

## Architecture

### Recommended Agent Structure
1. **Orchestrator Agent** - Routes customer inquiries to specialized agents
2. **Inventory Agent** - Checks stock levels, triggers reorders when necessary
3. **Quote Agent** - Generates quotes using historical data and bulk discounts
4. **Sales Agent** - Finalizes transactions based on inventory and delivery timelines

### Required Tools
- `check_inventory(paper_type)` - Query inventory for paper types
- `get_quote_history(customer_request)` - Retrieve historical quote data
- `check_delivery_timeline(item)` - Get supplier delivery estimates
- `fulfill_order(order_details)` - Update database for completed orders

## Tech Stack

- **Framework Options**: `smolagents`, `pydantic-ai`, or `npcpy` (choose one)
- **Database**: SQLite3
- **Language**: Python 3.x

## Key Files

| File | Purpose |
|------|---------|
| `project_starter.py` | Starter code with database init, inventory management, transaction tracking |
| `quote_requests_sample.csv` | Test dataset for validating agent system |
| `test_results.csv` | Output file for evaluation results |
| `beaver_agents.py` | Main implementation (single file submission) |

## Development Commands

```bash
# Run the multi-agent system
python beaver_agents.py

# Test with sample requests
python beaver_agents.py < quote_requests_sample.csv
```

## Database Schema (SQLite3)

The starter code manages:
- Inventory stock levels
- Financial transactions
- Quote history
- Supplier delivery estimates
- Cash balance tracking

## Deliverables

1. **Workflow diagram** (image file) - Agent interactions and data flows
2. **Source code** (`beaver_agents.py`) - Single Python file
3. **Documentation** - System explanation and requirement verification

## Testing Criteria

- Agents handle various customer inquiries and orders
- Orders optimize inventory use and profitability
- Quoting provides competitive and attractive pricing

## Active Technologies
- Python 3.x (compatible with smolagents framework) + smolagents (HuggingFace), sqlite3 (stdlib), pandas, sqlalchemy (001-beaver-agents)
- SQLite (`munder_difflin.db`) via SQLAlchemy (001-beaver-agents)

## Recent Changes
- 001-beaver-agents: Added Python 3.x (compatible with smolagents framework) + smolagents (HuggingFace), sqlite3 (stdlib), pandas, sqlalchemy
