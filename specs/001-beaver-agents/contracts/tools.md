# Tool Contracts: Beaver's Choice Paper Company

**Phase**: 1 - Design
**Date**: 2026-01-06
**Framework**: smolagents `@tool` decorator

## Overview

This document defines the interface contracts for all tools used by specialist agents. Each tool wraps helper functions from `project_starter.py` and provides a text-based interface for agent interaction.

---

## Inventory Agent Tools

### check_inventory

**Purpose**: Query current stock level for a specific item.

**Signature**:
```python
@tool
def check_inventory(item_name: str, as_of_date: str) -> str:
    """Check the current stock level for a specific paper product.

    Args:
        item_name: Exact name of the product (e.g., 'Glossy paper', 'Cardstock')
        as_of_date: Date to check inventory as of (ISO format: YYYY-MM-DD)

    Returns:
        A formatted string with item name, current stock, min threshold, and unit price.
        Returns error message if item not found.
    """
```

**Wraps**: `get_stock_level(item_name, as_of_date)`

**Example Response**:
```
Item: Glossy paper
Current Stock: 450 units
Minimum Threshold: 100 units
Unit Price: $0.20
Status: IN STOCK
```

**Error Cases**:
- Item not found: "Item 'Unknown Paper' not found in inventory."
- Invalid date: "Invalid date format. Please use YYYY-MM-DD."

---

### get_all_inventory

**Purpose**: Retrieve complete inventory snapshot.

**Signature**:
```python
@tool
def get_all_inventory(as_of_date: str) -> str:
    """Get a complete list of all items currently in stock.

    Args:
        as_of_date: Date to check inventory as of (ISO format: YYYY-MM-DD)

    Returns:
        A formatted table of all items with positive stock.
    """
```

**Wraps**: `get_all_inventory(as_of_date)`

**Example Response**:
```
INVENTORY AS OF 2025-04-01
==========================
Item                    | Stock | Unit Price
------------------------|-------|----------
A4 paper                | 500   | $0.05
Cardstock               | 350   | $0.15
Glossy paper            | 450   | $0.20
...
Total Items: 18
```

---

### trigger_reorder

**Purpose**: Create a stock order transaction to replenish inventory.

**Signature**:
```python
@tool
def trigger_reorder(item_name: str, quantity: int, order_date: str) -> str:
    """Place a reorder for inventory replenishment.

    Args:
        item_name: Exact name of the product to reorder
        quantity: Number of units to order
        order_date: Date of the order (ISO format: YYYY-MM-DD)

    Returns:
        Confirmation with order details and estimated delivery date.
    """
```

**Wraps**:
- `create_transaction(item_name, "stock_orders", quantity, price, date)`
- `get_supplier_delivery_date(order_date, quantity)`

**Example Response**:
```
REORDER CONFIRMED
=================
Item: Glossy paper
Quantity: 200 units
Cost: $40.00 (@ $0.20/unit)
Order Date: 2025-04-01
Estimated Delivery: 2025-04-02 (1 day lead time)
```

---

## Quote Agent Tools

### search_quote_history

**Purpose**: Find historical quotes for similar requests.

**Signature**:
```python
@tool
def search_quote_history(search_terms: str) -> str:
    """Search historical quotes for similar customer requests.

    Args:
        search_terms: Comma-separated keywords to search (e.g., 'glossy, conference, large')

    Returns:
        Up to 5 matching historical quotes with pricing and explanations.
    """
```

**Wraps**: `search_quote_history(search_terms.split(','), limit=5)`

**Example Response**:
```
MATCHING HISTORICAL QUOTES
==========================

1. Request: "500 sheets of glossy paper for conference"
   Total: $90.00
   Discount: 10% bulk discount applied
   Event: conference | Size: medium

2. Request: "300 sheets cardstock, 200 glossy for meeting"
   Total: $85.00
   Discount: Rounded total for convenience
   Event: meeting | Size: small

Found 2 matching quotes.
```

---

### get_item_price

**Purpose**: Lookup unit price for a specific item.

**Signature**:
```python
@tool
def get_item_price(item_name: str) -> str:
    """Get the unit price for a specific product.

    Args:
        item_name: Exact name of the product

    Returns:
        Item name and unit price, or error if not found.
    """
```

**Wraps**: Database query on inventory table

**Example Response**:
```
Item: Glossy paper
Unit Price: $0.20 per sheet
Category: paper
```

---

### calculate_quote

**Purpose**: Generate a complete quote with bulk discounts.

**Signature**:
```python
@tool
def calculate_quote(items_json: str) -> str:
    """Calculate a quote for multiple items with bulk discounts.

    Args:
        items_json: JSON string of items and quantities.
                    Format: [{"item": "Glossy paper", "quantity": 500}, ...]

    Returns:
        Detailed quote with itemized pricing, discounts, and total.
    """
```

**Example Input**:
```json
[
    {"item": "Glossy paper", "quantity": 500},
    {"item": "Cardstock", "quantity": 200}
]
```

**Example Response**:
```
QUOTE GENERATED
===============

Itemized Pricing:
-----------------
1. Glossy paper
   Quantity: 500 units @ $0.20 each
   Subtotal: $100.00
   Bulk Discount (10%): -$10.00
   Line Total: $90.00

2. Cardstock
   Quantity: 200 units @ $0.15 each
   Subtotal: $30.00
   Line Total: $30.00

-----------------
Subtotal: $120.00
Total Discount: $10.00
FINAL TOTAL: $120.00

Pricing Explanation:
Thank you for your order! We've applied a 10% bulk discount
on the glossy paper due to the quantity ordered. The final
total has been rounded to a convenient amount for your budget.
```

**Bulk Discount Rules**:
| Quantity | Discount |
|----------|----------|
| < 100 | 0% |
| 100-499 | 5% |
| 500-999 | 10% |
| 1000+ | 15% |

---

## Sales Agent Tools

### check_delivery_timeline

**Purpose**: Get estimated delivery date based on order quantity.

**Signature**:
```python
@tool
def check_delivery_timeline(quantity: int, order_date: str) -> str:
    """Estimate delivery date based on order quantity.

    Args:
        quantity: Number of units being ordered
        order_date: Date order is placed (ISO format: YYYY-MM-DD)

    Returns:
        Estimated delivery date with lead time explanation.
    """
```

**Wraps**: `get_supplier_delivery_date(order_date, quantity)`

**Delivery Schedule**:
| Quantity | Lead Time |
|----------|-----------|
| ≤10 | Same day |
| 11-100 | 1 day |
| 101-1000 | 4 days |
| >1000 | 7 days |

**Example Response**:
```
DELIVERY ESTIMATE
=================
Order Quantity: 500 units
Order Date: 2025-04-01
Lead Time: 4 business days
Estimated Delivery: 2025-04-05
```

---

### fulfill_order

**Purpose**: Record a sales transaction and update inventory.

**Signature**:
```python
@tool
def fulfill_order(item_name: str, quantity: int, price: float, order_date: str) -> str:
    """Record a completed sale and update inventory.

    Args:
        item_name: Exact name of the product sold
        quantity: Number of units sold
        price: Total sale price
        order_date: Date of sale (ISO format: YYYY-MM-DD)

    Returns:
        Confirmation with transaction ID and updated balances.
    """
```

**Wraps**: `create_transaction(item_name, "sales", quantity, price, date)`

**Example Response**:
```
ORDER FULFILLED
===============
Transaction ID: 42
Item: Glossy paper
Quantity: 500 units
Sale Price: $90.00
Date: 2025-04-01

Updated Balances:
- Cash Balance: $50,090.00
- Glossy paper Stock: 450 units (was 950)

Thank you for your order!
```

---

### get_cash_balance

**Purpose**: Check current cash balance.

**Signature**:
```python
@tool
def get_cash_balance(as_of_date: str) -> str:
    """Get the current cash balance as of a specific date.

    Args:
        as_of_date: Date to check balance (ISO format: YYYY-MM-DD)

    Returns:
        Current cash balance with breakdown.
    """
```

**Wraps**: `get_cash_balance(as_of_date)`

**Example Response**:
```
CASH BALANCE AS OF 2025-04-01
=============================
Available Cash: $48,500.00

Summary:
- Total Sales Revenue: $52,000.00
- Total Stock Purchases: $3,500.00
- Net Balance: $48,500.00
```

---

## Tool Error Handling

All tools follow consistent error response patterns:

### Standard Error Format
```
ERROR: [Error Type]
Description: [What went wrong]
Suggestion: [How to fix]
```

### Common Error Types

| Error | Trigger | Response |
|-------|---------|----------|
| ITEM_NOT_FOUND | Invalid item name | List similar items |
| INVALID_DATE | Malformed date | Show expected format |
| INSUFFICIENT_STOCK | Order > available | Show current stock |
| INSUFFICIENT_FUNDS | Reorder > cash | Show cash balance |
| INVALID_QUANTITY | Zero or negative | Require positive integer |

---

## Agent-Tool Mapping

| Agent | Tools | Responsibility |
|-------|-------|----------------|
| Inventory Agent | check_inventory, get_all_inventory, trigger_reorder | Stock management |
| Quote Agent | search_quote_history, get_item_price, calculate_quote | Pricing |
| Sales Agent | check_delivery_timeline, fulfill_order, get_cash_balance | Order processing |
| Orchestrator | None (delegates) | Routing & coordination |
