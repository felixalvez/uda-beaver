# Beaver's Choice Paper Company - Agent Workflow

## Multi-Agent Architecture

```mermaid
flowchart TD
    subgraph Customer["Customer Interaction"]
        INPUT[/"Customer Request"/]
        OUTPUT[/"Response"/]
    end

    subgraph Orchestrator["Orchestrator Agent (CodeAgent)"]
        ROUTE{Route Request}
        COMPILE[Compile Response]
    end

    subgraph Specialists["Specialist Agents (ToolCallingAgent)"]
        INV["Inventory Agent"]
        QUOTE["Quote Agent"]
        SALES["Sales Agent"]
    end

    subgraph Tools["Agent Tools"]
        INV_TOOLS["check_inventory<br/>get_all_inventory<br/>trigger_reorder"]
        QUOTE_TOOLS["get_item_price<br/>search_quote_history<br/>calculate_quote"]
        SALES_TOOLS["check_delivery_timeline<br/>fulfill_order<br/>get_cash_balance"]
    end

    subgraph Database["SQLite Database"]
        DB[(munder_difflin.db)]
    end

    INPUT --> ROUTE
    ROUTE --> INV
    ROUTE --> QUOTE
    ROUTE --> SALES

    INV --> INV_TOOLS
    QUOTE --> QUOTE_TOOLS
    SALES --> SALES_TOOLS

    INV_TOOLS --> DB
    QUOTE_TOOLS --> DB
    SALES_TOOLS --> DB

    INV --> COMPILE
    QUOTE --> COMPILE
    SALES --> COMPILE
    COMPILE --> OUTPUT

    style Orchestrator fill:#e1f5fe
    style Specialists fill:#f3e5f5
    style Tools fill:#fff3e0
    style Database fill:#e8f5e9
```

## Request Flow Sequence

```mermaid
sequenceDiagram
    participant C as Customer
    participant O as Orchestrator
    participant I as Inventory Agent
    participant Q as Quote Agent
    participant S as Sales Agent
    participant DB as Database

    C->>O: Natural language request

    Note over O: Analyze request type

    alt Inventory Query
        O->>I: Check stock
        I->>DB: get_stock_level()
        DB-->>I: Stock data
        I-->>O: Stock report
    end

    alt Quote Request
        O->>Q: Generate quote
        Q->>DB: search_quote_history()
        DB-->>Q: Historical data
        Q->>Q: calculate_quote()
        Q-->>O: Quote with discounts
    end

    alt Order Fulfillment
        O->>I: Pre-check inventory
        I->>DB: Check stock level
        alt Stock Below Threshold
            I->>DB: trigger_reorder()
        end
        I-->>O: Inventory status
        O->>S: Fulfill order
        S->>DB: create_transaction()
        S->>DB: get_delivery_timeline()
        S-->>O: Order confirmation
    end

    O-->>C: Compiled response
```

## State Transitions

```mermaid
stateDiagram-v2
    [*] --> RequestReceived: Customer inquiry
    RequestReceived --> Routing: Orchestrator analyzes

    Routing --> InventoryCheck: Stock query
    Routing --> QuoteGeneration: Price request
    Routing --> OrderFulfillment: Purchase order

    InventoryCheck --> LowStockDetected: Below threshold
    LowStockDetected --> ReorderTriggered: Auto-reorder
    ReorderTriggered --> ResponseCompiled
    InventoryCheck --> ResponseCompiled: Stock OK

    QuoteGeneration --> DiscountApplied: Bulk order
    DiscountApplied --> ResponseCompiled
    QuoteGeneration --> ResponseCompiled: Standard price

    OrderFulfillment --> PreFlightCheck: Verify stock
    PreFlightCheck --> SaleRecorded: Stock available
    PreFlightCheck --> ReorderTriggered: Need reorder
    SaleRecorded --> ResponseCompiled

    ResponseCompiled --> [*]: Return to customer
```

## Agent Configuration

| Agent | Type | Tools | Responsibility |
|-------|------|-------|----------------|
| Orchestrator | `CodeAgent` | None (delegates) | Route requests, compile responses |
| Inventory | `ToolCallingAgent` | 3 tools | Stock queries, reordering |
| Quote | `ToolCallingAgent` | 3 tools | Pricing, discounts |
| Sales | `ToolCallingAgent` | 3 tools | Order fulfillment |

## Tool-to-Helper Function Mapping

Each tool uses specific helper functions from the starter code (`project_starter.py`):

### Inventory Agent Tools

| Tool | Purpose | Helper Functions Used |
|------|---------|----------------------|
| `check_inventory` | Query stock level for a specific item | `get_stock_level()` |
| `get_all_inventory` | Get complete inventory snapshot | `get_all_inventory()` |
| `trigger_reorder` | Place replenishment order | `create_transaction()`, `get_cash_balance()`, `get_supplier_delivery_date()` |

### Quote Agent Tools

| Tool | Purpose | Helper Functions Used |
|------|---------|----------------------|
| `get_item_price` | Lookup unit price from catalog | None (uses in-memory catalog) |
| `search_quote_history` | Find similar historical quotes | `search_quote_history()` |
| `calculate_quote` | Generate itemized quote with discounts | None (calculation logic only) |

### Sales Agent Tools

| Tool | Purpose | Helper Functions Used |
|------|---------|----------------------|
| `check_delivery_timeline` | Estimate delivery based on quantity | `get_supplier_delivery_date()` |
| `fulfill_order` | Record sale and update inventory | `create_transaction()`, `get_stock_level()`, `get_cash_balance()`, `get_supplier_delivery_date()` |
| `get_cash_balance` | Get current cash position | `get_cash_balance()` |

### Test Harness Functions

| Function | Purpose | Helper Functions Used |
|----------|---------|----------------------|
| `run_test_scenarios()` | Process test dataset | `init_database()`, `generate_financial_report()` |

## Bulk Discount Tiers

| Quantity | Discount |
|----------|----------|
| < 100 | 0% |
| 100-499 | 5% |
| 500-999 | 10% |
| 1000+ | 15% |

## Delivery Lead Times

| Quantity | Lead Time |
|----------|-----------|
| ≤10 | Same day |
| 11-100 | 1 day |
| 101-1000 | 4 days |
| >1000 | 7 days |
