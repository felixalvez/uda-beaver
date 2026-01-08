# Tasks: Beaver's Choice Paper Company Multi-Agent System

**Input**: Design documents from `/specs/001-beaver-agents/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/tools.md, research.md, quickstart.md

**Tests**: Not explicitly requested in specification - omitting test tasks per template guidelines.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

This is a **single-file project** per constitution constraint V:
- All code in `beaver_agents.py` at repository root
- Reference code in `project-starter-ref-code/`
- Documentation in `docs/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, environment configuration, and file structure

- [ ] T001 Create `.env` file with API key placeholder in repository root
- [ ] T002 Create `.gitignore` with `.env`, `*.db`, `__pycache__/`, `*.pyc` entries in repository root
- [ ] T003 [P] Create `beaver_agents.py` skeleton with imports and docstring in repository root
- [ ] T004 [P] Create `docs/` directory and `docs/workflow.md` with Mermaid diagram from constitution

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Database & Configuration

- [ ] T005 Copy database helper functions from `project-starter-ref-code/project_starter.py` into `beaver_agents.py`
- [ ] T006 Implement environment configuration (load `.env`, validate API key) in `beaver_agents.py`
- [ ] T007 Initialize SQLAlchemy engine and call `init_database()` in `beaver_agents.py`

### smolagents Framework Setup

- [ ] T008 Import smolagents components (`tool`, `CodeAgent`, `ToolCallingAgent`) in `beaver_agents.py`
- [ ] T009 Configure LLM model instance with API key from environment in `beaver_agents.py`

### Product Catalog

- [ ] T010 Copy `paper_supplies` list (44 products with pricing) into `beaver_agents.py`

**Checkpoint**: Foundation ready - database initialized, smolagents configured, catalog loaded

---

## Phase 3: User Story 1 - Customer Quote Request (Priority: P1)

**Goal**: Generate quotes with itemized pricing, bulk discounts, and delivery estimates from natural language customer requests.

**Independent Test**: Submit "I need 500 sheets of glossy paper for a conference" and verify quote response with itemized pricing, 10% bulk discount, and rounded total.

### Tools for User Story 1

- [ ] T011 [P] [US1] Implement `@tool get_item_price(item_name: str) -> str` in `beaver_agents.py`
- [ ] T012 [P] [US1] Implement `@tool search_quote_history(search_terms: str) -> str` in `beaver_agents.py`
- [ ] T013 [US1] Implement bulk discount calculation helper function in `beaver_agents.py`
- [ ] T014 [US1] Implement `@tool calculate_quote(items_json: str) -> str` with bulk discounts in `beaver_agents.py`

### Quote Agent for User Story 1

- [ ] T015 [US1] Define Quote Agent system prompt with product catalog and discount rules in `beaver_agents.py`
- [ ] T016 [US1] Create `quote_agent = ToolCallingAgent(...)` with quote tools in `beaver_agents.py`

### Validation for User Story 1

- [ ] T017 [US1] Test Quote Agent standalone with sample request in `beaver_agents.py`
- [ ] T018 [US1] Verify bulk discount tiers: 0% (<100), 5% (100-499), 10% (500-999), 15% (1000+) in `beaver_agents.py`

**Checkpoint**: Quote Agent functional - can generate itemized quotes with bulk discounts

---

## Phase 4: User Story 2 - Inventory Check and Autonomous Reordering (Priority: P2)

**Goal**: Query stock levels and autonomously trigger reorders when inventory falls below minimum thresholds.

**Independent Test**: Call `check_inventory("Glossy paper", "2025-04-01")` and verify stock level, threshold, and price are returned. Simulate low stock scenario and verify reorder transaction is created.

### Tools for User Story 2

- [ ] T019 [P] [US2] Implement `@tool check_inventory(item_name: str, as_of_date: str) -> str` in `beaver_agents.py`
- [ ] T020 [P] [US2] Implement `@tool get_all_inventory(as_of_date: str) -> str` in `beaver_agents.py`
- [ ] T021 [US2] Implement `@tool trigger_reorder(item_name: str, quantity: int, order_date: str) -> str` in `beaver_agents.py`

### Inventory Agent for User Story 2

- [ ] T022 [US2] Define Inventory Agent system prompt with reorder logic in `beaver_agents.py`
- [ ] T023 [US2] Create `inventory_agent = ToolCallingAgent(...)` with inventory tools in `beaver_agents.py`

### Validation for User Story 2

- [ ] T024 [US2] Test Inventory Agent standalone with stock check request in `beaver_agents.py`
- [ ] T025 [US2] Verify autonomous reorder triggers when stock < min_stock_level in `beaver_agents.py`

**Checkpoint**: Inventory Agent functional - can check stock and trigger reorders

---

## Phase 5: User Story 3 - Sales Order Fulfillment (Priority: P3)

**Goal**: Process confirmed orders by recording sales transactions, updating inventory, and providing delivery estimates.

**Independent Test**: Submit order fulfillment for 100 units of Cardstock and verify: (1) sales transaction recorded, (2) cash balance increased, (3) inventory decreased, (4) delivery estimate returned.

### Tools for User Story 3

- [ ] T026 [P] [US3] Implement `@tool check_delivery_timeline(quantity: int, order_date: str) -> str` in `beaver_agents.py`
- [ ] T027 [P] [US3] Implement `@tool get_cash_balance(as_of_date: str) -> str` in `beaver_agents.py`
- [ ] T028 [US3] Implement pre-fulfillment reorder check helper in `beaver_agents.py`
- [ ] T029 [US3] Implement `@tool fulfill_order(item_name: str, quantity: int, price: float, order_date: str) -> str` in `beaver_agents.py`

### Sales Agent for User Story 3

- [ ] T030 [US3] Define Sales Agent system prompt with fulfillment workflow in `beaver_agents.py`
- [ ] T031 [US3] Create `sales_agent = ToolCallingAgent(...)` with sales tools in `beaver_agents.py`

### Integration for User Story 3

- [ ] T032 [US3] Integrate pre-fulfillment inventory check (call Inventory Agent before sale) in `beaver_agents.py`
- [ ] T033 [US3] Test Sales Agent standalone with order fulfillment request in `beaver_agents.py`

**Checkpoint**: Sales Agent functional - can fulfill orders with delivery estimates and reorder triggers

---

## Phase 6: User Story 4 - Multi-Agent Orchestration (Priority: P4)

**Goal**: Route customer inquiries to appropriate specialist agents and compile coherent responses.

**Independent Test**: Submit "Check if you have glossy paper, quote me 500 sheets, and process my order" and verify orchestrator routes to Inventory → Quote → Sales agents in sequence.

### Orchestrator Agent for User Story 4

- [ ] T034 [US4] Define Orchestrator system prompt with routing logic in `beaver_agents.py`
- [ ] T035 [US4] Create `orchestrator = CodeAgent(managed_agents=[inventory_agent, quote_agent, sales_agent])` in `beaver_agents.py`

### Error Handling for User Story 4

- [ ] T036 [US4] Implement graceful error handling for unknown items in `beaver_agents.py`
- [ ] T037 [US4] Implement graceful error handling for insufficient stock in `beaver_agents.py`
- [ ] T038 [US4] Implement graceful error handling for invalid inputs in `beaver_agents.py`

### Validation for User Story 4

- [ ] T039 [US4] Test Orchestrator with single-agent requests (inventory only, quote only, sales only) in `beaver_agents.py`
- [ ] T040 [US4] Test Orchestrator with multi-agent request requiring all three specialists in `beaver_agents.py`

**Checkpoint**: Full multi-agent system operational

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, testing, and deliverable preparation

### Test Harness

- [ ] T041 Implement `run_test_scenarios()` function to process `quote_requests_sample.csv` in `beaver_agents.py`
- [ ] T042 Add progress logging and financial report output to `run_test_scenarios()` in `beaver_agents.py`
- [ ] T043 Generate `test_results.csv` from test scenario execution in repository root

### Documentation

- [ ] T044 [P] Export `docs/workflow.md` Mermaid diagram to `workflow.png` using mermaid-cli or mermaid.live
- [ ] T045 [P] Add comprehensive docstrings to all tools and agents in `beaver_agents.py`
- [ ] T046 Create final documentation explaining system design in `README.md` or submission doc

### Final Validation

- [ ] T047 Run all 20 test scenarios and verify no critical errors in `beaver_agents.py`
- [ ] T048 Verify agent count is exactly 4 (Orchestrator + 3 specialists) in `beaver_agents.py`
- [ ] T049 Verify all responses are text-only (no GUI, no binary data) in `beaver_agents.py`
- [ ] T050 Run constitution compliance check against all principles in `beaver_agents.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Quote Agent
- **User Story 2 (Phase 4)**: Depends on Foundational - Inventory Agent
- **User Story 3 (Phase 5)**: Depends on Foundational + US1 + US2 - Sales Agent
- **User Story 4 (Phase 6)**: Depends on US1 + US2 + US3 - Orchestrator
- **Polish (Phase 7)**: Depends on all user stories complete

### User Story Dependencies

```
Foundational (Phase 2)
        │
        ├──────────────────┬──────────────────┐
        ▼                  ▼                  │
   User Story 1       User Story 2           │
   (Quote Agent)      (Inventory Agent)      │
        │                  │                 │
        └────────┬─────────┘                 │
                 ▼                           │
            User Story 3 ◄───────────────────┘
            (Sales Agent)
                 │
                 ▼
            User Story 4
            (Orchestrator)
```

### Within Each User Story

1. Tools first (marked [P] can be parallel within same phase)
2. Agent definition after tools
3. Validation after agent
4. Story complete before integration with later stories

### Parallel Opportunities

Within Phase 3 (US1):
- T011 and T012 can run in parallel (different tools)

Within Phase 4 (US2):
- T019 and T020 can run in parallel (different tools)

Within Phase 5 (US3):
- T026 and T027 can run in parallel (different tools)

Within Phase 7 (Polish):
- T044 and T045 can run in parallel (different concerns)

---

## Parallel Example: User Story 1

```bash
# Launch tool implementations in parallel:
Task: "T011 [P] [US1] Implement @tool get_item_price in beaver_agents.py"
Task: "T012 [P] [US1] Implement @tool search_quote_history in beaver_agents.py"

# Then sequential:
Task: "T013 [US1] Implement bulk discount helper"
Task: "T014 [US1] Implement @tool calculate_quote"
Task: "T015 [US1] Define Quote Agent system prompt"
Task: "T016 [US1] Create quote_agent"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T010)
3. Complete Phase 3: User Story 1 (T011-T018)
4. **STOP and VALIDATE**: Test Quote Agent with sample requests
5. Can demo quote generation capability

### Incremental Delivery

1. Setup + Foundational → Framework ready
2. Add User Story 1 → Quote Agent functional (MVP!)
3. Add User Story 2 → Inventory Agent functional
4. Add User Story 3 → Sales Agent functional
5. Add User Story 4 → Full orchestration
6. Polish → Deliverables complete

### Full System Build

1. Complete all phases sequentially
2. Run full test suite (20 scenarios)
3. Generate all deliverables:
   - `beaver_agents.py` (source code)
   - `workflow.png` (diagram)
   - `test_results.csv` (evaluation output)
   - Documentation

---

## Notes

- All code goes in single file `beaver_agents.py` per constitution constraint
- [P] tasks = different tools/concerns, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently testable after completion
- Commit after each phase or logical group of tasks
- Stop at any checkpoint to validate functionality
- Single-file constraint means careful organization within `beaver_agents.py`:
  1. Imports and configuration
  2. Database helpers (copied from starter)
  3. Product catalog
  4. Tool definitions
  5. Agent definitions
  6. Orchestrator
  7. Test harness
  8. Main entry point
