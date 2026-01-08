# Feature Specification: Beaver's Choice Paper Company Multi-Agent System

**Feature Branch**: `001-beaver-agents`
**Created**: 2026-01-06
**Status**: Draft
**Input**: User description: "Multi-agent system for Beaver's Choice Paper Company (Munder Difflin) handling inventory management, quote generation, and sales transaction fulfillment. Uses smolagents framework with max 5 agents. Must handle: (1) Inventory queries and autonomous reordering when stock falls below thresholds, (2) Quote generation with bulk discounts using historical data, (3) Sales order fulfillment with delivery timeline estimates. Text-only I/O, SQLite database, single-file deliverable (beaver_agents.py). Design decisions: LLM fuzzy matching for item names, pre-fulfillment reorder checks, quote out-of-stock items with supplier lead time."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Customer Quote Request (Priority: P1)

A customer contacts Beaver's Choice Paper Company requesting a quote for paper supplies. The customer describes their needs in natural language (e.g., "I need 500 sheets of glossy paper and 200 sheets of cardstock for a conference"). The system interprets the request, matches items to available inventory, calculates pricing with appropriate bulk discounts, and returns a detailed quote explaining the costs.

**Why this priority**: Quote generation is the primary business function - it drives revenue. Without quotes, no sales can occur. This represents the core value proposition of the system.

**Independent Test**: Can be fully tested by submitting a customer request and verifying that a quote is returned with itemized pricing, bulk discounts, and a total. Delivers immediate business value by automating the quoting process.

**Acceptance Scenarios**:

1. **Given** a customer request for paper supplies with specific quantities, **When** all items are in stock, **Then** the system returns a quote with itemized pricing, applicable bulk discounts, and a rounded total within 30 seconds.

2. **Given** a customer request using informal item names (e.g., "A4 glossy paper"), **When** the system processes the request, **Then** it correctly maps the informal name to the exact database item name (e.g., "Glossy paper") and includes it in the quote.

3. **Given** a customer request for items not currently in stock, **When** the system processes the request, **Then** it provides a quote that includes supplier lead time and estimated delivery date for those items.

4. **Given** a customer request with quantities exceeding bulk thresholds, **When** the quote is generated, **Then** the system applies appropriate bulk discounts and explains the discount reasoning in the quote response.

---

### User Story 2 - Inventory Check and Autonomous Reordering (Priority: P2)

A warehouse manager or the system itself needs to monitor stock levels. When inventory for any item falls below its minimum threshold (either through a sale or during a routine check), the system autonomously triggers a reorder from the supplier to replenish stock. The system tracks all inventory movements through transactions.

**Why this priority**: Inventory management prevents stockouts and ensures the business can fulfill orders. It's essential for operational continuity but depends on having the quote system in place first.

**Independent Test**: Can be tested by checking current stock levels for any item and verifying accurate counts. Autonomous reordering can be tested by simulating a sale that drops stock below threshold and verifying a reorder transaction is created.

**Acceptance Scenarios**:

1. **Given** a request to check inventory for a specific paper type, **When** the system queries the database, **Then** it returns the current stock level, minimum threshold, and unit price.

2. **Given** a sales transaction that would reduce stock below the minimum threshold, **When** the transaction is about to be processed, **Then** the system first creates a stock reorder transaction before completing the sale.

3. **Given** a stock reorder is triggered, **When** the reorder is created, **Then** the system records the transaction with item name, quantity, cost, and estimated delivery date from the supplier.

4. **Given** a request to view all inventory, **When** the system queries stock levels as of a specific date, **Then** it returns a complete list of items with positive stock quantities.

---

### User Story 3 - Sales Order Fulfillment (Priority: P3)

A customer confirms their order after receiving a quote. The sales agent processes the order by verifying inventory availability, calculating the final price, recording the sales transaction, and providing confirmation with an estimated delivery date.

**Why this priority**: Order fulfillment completes the sales cycle. It depends on both quoting (P1) and inventory management (P2) being functional, making it the natural final step.

**Independent Test**: Can be tested by submitting an order for in-stock items and verifying that a sales transaction is recorded, inventory is decremented, and a confirmation with delivery estimate is returned.

**Acceptance Scenarios**:

1. **Given** a confirmed order for items in stock, **When** the order is processed, **Then** a sales transaction is recorded with item name, quantity, price, and transaction date.

2. **Given** an order for items requiring supplier fulfillment, **When** the system calculates delivery, **Then** it provides an accurate estimate based on order quantity (same-day for small orders, up to 7 days for large orders).

3. **Given** a successful order fulfillment, **When** the transaction is complete, **Then** the cash balance increases by the sale amount and inventory decreases by the quantity sold.

4. **Given** an order that would exceed available cash balance for required reorders, **When** the system evaluates the order, **Then** it alerts the user to insufficient funds before processing.

---

### User Story 4 - Multi-Agent Orchestration (Priority: P4)

A customer submits a complex inquiry that requires coordination between multiple capabilities (e.g., "Can you check if you have glossy paper in stock, give me a quote for 1000 sheets, and process my order?"). The orchestrator agent routes the request to the appropriate specialist agents and compiles a coherent response.

**Why this priority**: Orchestration ties all capabilities together into a seamless experience. It requires all other stories to be functional first.

**Independent Test**: Can be tested by submitting a multi-part request and verifying that the system correctly routes to inventory, quote, and sales agents as needed, returning a unified response.

**Acceptance Scenarios**:

1. **Given** a customer inquiry, **When** the orchestrator receives it, **Then** it correctly identifies which specialist agent(s) should handle the request.

2. **Given** a request requiring multiple agents, **When** processing is complete, **Then** the orchestrator compiles responses from all agents into a single coherent text response.

3. **Given** an error from a specialist agent, **When** the orchestrator receives the error, **Then** it provides a helpful error message to the customer without exposing system internals.

---

### Edge Cases

- **Unknown Item Requested**: When a customer requests an item that doesn't exist in the product catalog, the system should list similar available items or indicate the item is not available.

- **Zero Stock Scenario**: When stock is completely depleted and customer needs immediate fulfillment, the system should explain the supplier lead time and offer alternatives.

- **Bulk Discount Edge Cases**: Orders exactly at discount thresholds should receive the discount (e.g., 100 units qualifies for bulk pricing, not 101+).

- **Date Parsing Failures**: When customer provides dates in unusual formats, the system should attempt to interpret them or ask for clarification.

- **Negative Quantities**: Requests with zero or negative quantities should be rejected with a clear error message.

- **Cash Balance Insufficient**: When reordering would exceed available cash, the system should prioritize critical items or alert for manual intervention.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST route customer inquiries to the appropriate specialist agent based on the nature of the request (inventory, quote, or sales).

- **FR-002**: System MUST match informal item names from customer requests to exact database item names using intelligent interpretation.

- **FR-003**: System MUST calculate quotes using base unit prices from the inventory and apply bulk discounts for qualifying quantities.

- **FR-004**: System MUST reference historical quote data when generating new quotes to ensure competitive and consistent pricing.

- **FR-005**: System MUST check current inventory levels before fulfilling any order.

- **FR-006**: System MUST autonomously trigger stock reorders when inventory falls below the item's minimum stock threshold during pre-fulfillment checks.

- **FR-007**: System MUST record all inventory movements as transactions (stock orders for incoming, sales for outgoing).

- **FR-008**: System MUST calculate delivery timelines based on order quantity (same-day to 7 days depending on size).

- **FR-009**: System MUST provide text-only responses to all customer inquiries (no graphical elements).

- **FR-010**: System MUST operate with a maximum of 5 agents total.

- **FR-011**: System MUST persist all data to the SQLite database and make decisions based on current database state.

- **FR-012**: System MUST handle out-of-stock items by calculating quotes with supplier lead time included.

- **FR-013**: System MUST round quote totals to psychologically appealing numbers (e.g., $50, $100) while explaining the discount.

- **FR-014**: System MUST track cash balance (revenue from sales minus costs from stock orders) and ensure sufficient funds for operations.

### Key Entities

- **Inventory Item**: Represents a product in the catalog with item name, category (paper/product/large_format/specialty), unit price, current stock level (calculated from transactions), and minimum stock threshold.

- **Transaction**: A record of inventory movement with item name, transaction type (stock_orders or sales), quantity, price, and transaction date. Used to calculate both inventory levels and cash balance.

- **Quote**: A pricing proposal for a customer request containing total amount, explanation of pricing/discounts, and metadata about job type, order size, and event type.

- **Quote Request**: A customer inquiry containing the request text, job role, order size category, event type, and request date.

### Assumptions

- Initial cash balance is $50,000 as seeded by the starter database.
- Approximately 40% of the product catalog is initially stocked (coverage controlled by seed).
- Bulk discount thresholds follow industry standard tiers (10+ units, 100+ units, 1000+ units).
- Supplier delivery lead times are fixed: same-day (<=10 units), 1 day (11-100), 4 days (101-1000), 7 days (>1000).
- All agent responses must be in English.
- The system operates in a single timezone (dates are ISO formatted).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Customer quote requests receive a complete response (itemized pricing, discounts, total, delivery estimate) within 60 seconds.

- **SC-002**: 90% of customer item references are correctly matched to database item names without manual clarification.

- **SC-003**: All sales transactions correctly update both cash balance and inventory levels in the database.

- **SC-004**: Autonomous reordering triggers 100% of the time when a sale would drop stock below minimum threshold.

- **SC-005**: System processes all 20 test scenarios from the sample dataset without critical errors.

- **SC-006**: Quote pricing is competitive with historical quotes for similar order types (within 20% variance for comparable orders).

- **SC-007**: System operates with exactly 4 agents (1 orchestrator + 3 specialists), well under the 5-agent maximum.

- **SC-008**: All customer interactions are handled via text-only input and output with no binary data or graphical elements.

- **SC-009**: Financial reports accurately reflect cumulative transactions (cash balance = sum of sales - sum of stock orders).

- **SC-010**: System correctly estimates delivery dates based on order quantity for 100% of fulfilled orders.
