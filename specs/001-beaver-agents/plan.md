# Implementation Plan: Beaver's Choice Paper Company Multi-Agent System

**Branch**: `001-beaver-agents` | **Date**: 2026-01-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-beaver-agents/spec.md`

## Summary

Build a multi-agent system for Beaver's Choice Paper Company (Munder Difflin) that handles customer inquiries for paper supplies. The system uses 4 agents (Orchestrator + Inventory + Quote + Sales) built with the smolagents framework, backed by SQLite for persistent data. Key capabilities include inventory queries with autonomous reordering, quote generation with bulk discounts based on historical data, and sales order fulfillment with delivery timeline estimates.

## Technical Context

**Language/Version**: Python 3.x (compatible with smolagents framework)
**Primary Dependencies**: smolagents (HuggingFace), sqlite3 (stdlib), pandas, sqlalchemy
**Storage**: SQLite (`munder_difflin.db`) via SQLAlchemy
**Testing**: Manual testing with `quote_requests_sample.csv` (20 test scenarios)
**Target Platform**: Local Python runtime (CLI-based)
**Project Type**: Single file (`beaver_agents.py`)
**Performance Goals**: Quote responses within 60 seconds
**Constraints**: Max 5 agents, text-only I/O, single-file deliverable
**Scale/Scope**: 20 test requests, ~44 product types, ~18 stocked items

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Agent Economy (5 max) | PASS | Design uses 4 agents: Orchestrator, Inventory, Quote, Sales |
| II. Text-Only Interface | PASS | All responses are text strings, no GUI |
| III. Database-Driven Decisions | PASS | All tools query SQLite for current state |
| IV. Tool-Agent Architecture | PASS | Each specialist has defined tools wrapping starter functions |
| V. Single-File Deliverable | PASS | All code in `beaver_agents.py` |
| VI. Simplicity First (KISS) | PASS | Direct tool implementations, no abstractions |
| VII. No Repetition (DRY) | PASS | Helper functions from starter code reused |
| VIII. Human Readability | PASS | PEP 8, descriptive names, documented prompts |
| IX. Security First | PASS | API keys from .env, no hardcoded secrets |
| Framework: smolagents | PASS | Selected framework per constitution |
| Diagramming: Mermaid | PASS | Workflow diagram in Mermaid format |

**GATE RESULT**: ALL PASSED - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-beaver-agents/
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Getting started guide
├── contracts/           # Phase 1: Tool interfaces
│   └── tools.md         # Tool specifications
└── tasks.md             # Phase 2: Implementation tasks
```

### Source Code (repository root)

```text
.
├── beaver_agents.py              # Main deliverable (single-file)
├── project-starter-ref-code/     # Reference starter code
│   ├── project_starter.py        # Helper functions to wrap
│   ├── quote_requests_sample.csv # Test dataset (20 scenarios)
│   ├── quote_requests.csv        # Historical requests for DB
│   ├── quotes.csv                # Historical quotes for DB
│   └── README.md                 # Starter documentation
├── docs/
│   └── workflow.md               # Mermaid diagram source
├── workflow.png                  # Exported diagram (deliverable)
├── test_results.csv              # Test output (deliverable)
└── .env                          # API keys (not committed)
```

**Structure Decision**: Single-file project per constitution constraint V. All agent code, tools, and orchestration in `beaver_agents.py`. Reference `project_starter.py` for helper functions.

## Complexity Tracking

> No violations - design complies with all constitution principles.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
