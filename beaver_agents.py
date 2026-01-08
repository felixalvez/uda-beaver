"""
Beaver's Choice Paper Company - Multi-Agent System
===================================================

A multi-agent system for handling inventory management, quote generation,
and sales transaction fulfillment using the smolagents framework.

Architecture:
- Orchestrator Agent (CodeAgent): Routes customer inquiries to specialists
- Inventory Agent (ToolCallingAgent): Stock queries and autonomous reordering
- Quote Agent (ToolCallingAgent): Pricing with bulk discounts
- Sales Agent (ToolCallingAgent): Order fulfillment and delivery estimates

Framework: smolagents (HuggingFace)
Database: SQLite via SQLAlchemy
"""

# =============================================================================
# IMPORTS
# =============================================================================

import os
import json
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Union
from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from sqlalchemy.sql import text

# smolagents framework imports
from smolagents import tool, CodeAgent, ToolCallingAgent, LiteLLMModel
from smolagents.agents import PromptTemplates

# Default templates for managed agents (required by smolagents)
DEFAULT_MANAGED_AGENT_TEMPLATE = {
    "task": """You're a helpful agent named '{{name}}'.
You have been submitted this task by your manager.
---
Task:
{{task}}
---
You're helping your manager solve a wider task: so make sure to not provide a one-line answer, but give as much information as possible to give them a clear understanding of the answer.""",
    "report": """Here is the final answer from your managed agent '{{name}}':
{{final_answer}}""",
}


def make_prompt_templates(system_prompt: str) -> PromptTemplates:
    """Create prompt_templates dict with custom system_prompt and proper defaults."""
    return {
        "system_prompt": system_prompt,
        "planning": {
            "initial_plan": "",
            "update_plan_pre_messages": "",
            "update_plan_post_messages": "",
        },
        "managed_agent": DEFAULT_MANAGED_AGENT_TEMPLATE,
        "final_answer": {"pre_messages": "", "post_messages": ""},
    }

# =============================================================================
# CONFIGURATION
# =============================================================================

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file")

# Database setup
db_engine = create_engine("sqlite:///munder_difflin.db")

# Configure LLM model
# Supports OpenAI models via LiteLLM (gpt-4, gpt-3.5-turbo) or Anthropic (claude-3-sonnet)
if os.getenv("OPENAI_API_KEY"):
    model = LiteLLMModel(model_id="gpt-4o-mini")
else:
    model = LiteLLMModel(model_id="claude-3-5-sonnet-20241022")

# =============================================================================
# PRODUCT CATALOG (44 items)
# =============================================================================

paper_supplies = [
    # Paper Types (priced per sheet unless specified)
    {"item_name": "A4 paper",                         "category": "paper",        "unit_price": 0.05},
    {"item_name": "Letter-sized paper",              "category": "paper",        "unit_price": 0.06},
    {"item_name": "Cardstock",                        "category": "paper",        "unit_price": 0.15},
    {"item_name": "Colored paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Glossy paper",                     "category": "paper",        "unit_price": 0.20},
    {"item_name": "Matte paper",                      "category": "paper",        "unit_price": 0.18},
    {"item_name": "Recycled paper",                   "category": "paper",        "unit_price": 0.08},
    {"item_name": "Eco-friendly paper",               "category": "paper",        "unit_price": 0.12},
    {"item_name": "Poster paper",                     "category": "paper",        "unit_price": 0.25},
    {"item_name": "Banner paper",                     "category": "paper",        "unit_price": 0.30},
    {"item_name": "Kraft paper",                      "category": "paper",        "unit_price": 0.10},
    {"item_name": "Construction paper",               "category": "paper",        "unit_price": 0.07},
    {"item_name": "Wrapping paper",                   "category": "paper",        "unit_price": 0.15},
    {"item_name": "Glitter paper",                    "category": "paper",        "unit_price": 0.22},
    {"item_name": "Decorative paper",                 "category": "paper",        "unit_price": 0.18},
    {"item_name": "Letterhead paper",                 "category": "paper",        "unit_price": 0.12},
    {"item_name": "Legal-size paper",                 "category": "paper",        "unit_price": 0.08},
    {"item_name": "Crepe paper",                      "category": "paper",        "unit_price": 0.05},
    {"item_name": "Photo paper",                      "category": "paper",        "unit_price": 0.25},
    {"item_name": "Uncoated paper",                   "category": "paper",        "unit_price": 0.06},
    {"item_name": "Butcher paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Heavyweight paper",                "category": "paper",        "unit_price": 0.20},
    {"item_name": "Standard copy paper",              "category": "paper",        "unit_price": 0.04},
    {"item_name": "Bright-colored paper",             "category": "paper",        "unit_price": 0.12},
    {"item_name": "Patterned paper",                  "category": "paper",        "unit_price": 0.15},
    # Product Types (priced per unit)
    {"item_name": "Paper plates",                     "category": "product",      "unit_price": 0.10},
    {"item_name": "Paper cups",                       "category": "product",      "unit_price": 0.08},
    {"item_name": "Paper napkins",                    "category": "product",      "unit_price": 0.02},
    {"item_name": "Disposable cups",                  "category": "product",      "unit_price": 0.10},
    {"item_name": "Table covers",                     "category": "product",      "unit_price": 1.50},
    {"item_name": "Envelopes",                        "category": "product",      "unit_price": 0.05},
    {"item_name": "Sticky notes",                     "category": "product",      "unit_price": 0.03},
    {"item_name": "Notepads",                         "category": "product",      "unit_price": 2.00},
    {"item_name": "Invitation cards",                 "category": "product",      "unit_price": 0.50},
    {"item_name": "Flyers",                           "category": "product",      "unit_price": 0.15},
    {"item_name": "Party streamers",                  "category": "product",      "unit_price": 0.05},
    {"item_name": "Decorative adhesive tape (washi tape)", "category": "product", "unit_price": 0.20},
    {"item_name": "Paper party bags",                 "category": "product",      "unit_price": 0.25},
    {"item_name": "Name tags with lanyards",          "category": "product",      "unit_price": 0.75},
    {"item_name": "Presentation folders",             "category": "product",      "unit_price": 0.50},
    # Large-format items (priced per unit)
    {"item_name": "Large poster paper (24x36 inches)", "category": "large_format", "unit_price": 1.00},
    {"item_name": "Rolls of banner paper (36-inch width)", "category": "large_format", "unit_price": 2.50},
    # Specialty papers
    {"item_name": "100 lb cover stock",               "category": "specialty",    "unit_price": 0.50},
    {"item_name": "80 lb text paper",                 "category": "specialty",    "unit_price": 0.40},
    {"item_name": "250 gsm cardstock",                "category": "specialty",    "unit_price": 0.30},
    {"item_name": "220 gsm poster paper",             "category": "specialty",    "unit_price": 0.35},
]

# =============================================================================
# DATABASE HELPER FUNCTIONS (from project_starter.py)
# =============================================================================

def generate_sample_inventory(paper_supplies: list, coverage: float = 0.4, seed: int = 137) -> pd.DataFrame:
    """Generate inventory for a percentage of items from the paper supply list."""
    np.random.seed(seed)
    num_items = int(len(paper_supplies) * coverage)
    selected_indices = np.random.choice(range(len(paper_supplies)), size=num_items, replace=False)
    selected_items = [paper_supplies[i] for i in selected_indices]

    inventory = []
    for item in selected_items:
        inventory.append({
            "item_name": item["item_name"],
            "category": item["category"],
            "unit_price": item["unit_price"],
            "current_stock": np.random.randint(200, 800),
            "min_stock_level": np.random.randint(50, 150)
        })
    return pd.DataFrame(inventory)


def init_database(engine: Engine = None, seed: int = 137) -> Engine:
    """Initialize the Munder Difflin database with tables and seed data."""
    global db_engine
    if engine is None:
        engine = db_engine

    try:
        # Create transactions table schema
        transactions_schema = pd.DataFrame({
            "id": [], "item_name": [], "transaction_type": [],
            "units": [], "price": [], "transaction_date": [],
        })
        transactions_schema.to_sql("transactions", engine, if_exists="replace", index=False)

        initial_date = datetime(2025, 1, 1).isoformat()

        # Load quote requests from CSV
        quote_requests_path = "project-starter-ref-code/quote_requests.csv"
        if os.path.exists(quote_requests_path):
            quote_requests_df = pd.read_csv(quote_requests_path)
            quote_requests_df["id"] = range(1, len(quote_requests_df) + 1)
            quote_requests_df.to_sql("quote_requests", engine, if_exists="replace", index=False)

        # Load quotes from CSV
        quotes_path = "project-starter-ref-code/quotes.csv"
        if os.path.exists(quotes_path):
            import ast
            quotes_df = pd.read_csv(quotes_path)
            quotes_df["request_id"] = range(1, len(quotes_df) + 1)
            quotes_df["order_date"] = initial_date

            if "request_metadata" in quotes_df.columns:
                quotes_df["request_metadata"] = quotes_df["request_metadata"].apply(
                    lambda x: ast.literal_eval(x) if isinstance(x, str) else x
                )
                quotes_df["job_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("job_type", ""))
                quotes_df["order_size"] = quotes_df["request_metadata"].apply(lambda x: x.get("order_size", ""))
                quotes_df["event_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("event_type", ""))

            quotes_df = quotes_df[["request_id", "total_amount", "quote_explanation",
                                   "order_date", "job_type", "order_size", "event_type"]]
            quotes_df.to_sql("quotes", engine, if_exists="replace", index=False)

        # Generate and seed inventory
        inventory_df = generate_sample_inventory(paper_supplies, seed=seed)

        initial_transactions = []
        # Seed initial cash balance ($50,000)
        initial_transactions.append({
            "item_name": None, "transaction_type": "sales",
            "units": None, "price": 50000.0, "transaction_date": initial_date,
        })

        # Add stock orders for each inventory item
        for _, item in inventory_df.iterrows():
            initial_transactions.append({
                "item_name": item["item_name"],
                "transaction_type": "stock_orders",
                "units": item["current_stock"],
                "price": item["current_stock"] * item["unit_price"],
                "transaction_date": initial_date,
            })

        pd.DataFrame(initial_transactions).to_sql("transactions", engine, if_exists="append", index=False)
        inventory_df.to_sql("inventory", engine, if_exists="replace", index=False)

        return engine
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise


def create_transaction(item_name: str, transaction_type: str, quantity: int,
                       price: float, date: Union[str, datetime]) -> int:
    """Record a transaction (stock_orders or sales) in the database."""
    try:
        date_str = date.isoformat() if isinstance(date, datetime) else date
        if transaction_type not in {"stock_orders", "sales"}:
            raise ValueError("Transaction type must be 'stock_orders' or 'sales'")

        transaction = pd.DataFrame([{
            "item_name": item_name, "transaction_type": transaction_type,
            "units": quantity, "price": price, "transaction_date": date_str,
        }])
        transaction.to_sql("transactions", db_engine, if_exists="append", index=False)

        result = pd.read_sql("SELECT last_insert_rowid() as id", db_engine)
        return int(result.iloc[0]["id"])
    except Exception as e:
        print(f"Error creating transaction: {e}")
        raise


def get_all_inventory_db(as_of_date: str) -> Dict[str, int]:
    """Retrieve inventory snapshot as of a specific date."""
    query = """
        SELECT item_name,
            SUM(CASE WHEN transaction_type = 'stock_orders' THEN units
                     WHEN transaction_type = 'sales' THEN -units ELSE 0 END) as stock
        FROM transactions
        WHERE item_name IS NOT NULL AND transaction_date <= :as_of_date
        GROUP BY item_name HAVING stock > 0
    """
    result = pd.read_sql(query, db_engine, params={"as_of_date": as_of_date})
    return dict(zip(result["item_name"], result["stock"]))


def get_stock_level(item_name: str, as_of_date: Union[str, datetime]) -> pd.DataFrame:
    """Get stock level of a specific item as of a date."""
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    query = """
        SELECT item_name,
            COALESCE(SUM(CASE WHEN transaction_type = 'stock_orders' THEN units
                              WHEN transaction_type = 'sales' THEN -units ELSE 0 END), 0) AS current_stock
        FROM transactions
        WHERE item_name = :item_name AND transaction_date <= :as_of_date
    """
    return pd.read_sql(query, db_engine, params={"item_name": item_name, "as_of_date": as_of_date})


def get_supplier_delivery_date(input_date_str: str, quantity: int) -> str:
    """Calculate supplier delivery date based on order quantity."""
    try:
        input_date_dt = datetime.fromisoformat(input_date_str.split("T")[0])
    except (ValueError, TypeError):
        input_date_dt = datetime.now()

    if quantity <= 10:
        days = 0
    elif quantity <= 100:
        days = 1
    elif quantity <= 1000:
        days = 4
    else:
        days = 7

    return (input_date_dt + timedelta(days=days)).strftime("%Y-%m-%d")


def get_cash_balance_db(as_of_date: Union[str, datetime]) -> float:
    """Calculate cash balance as of a specific date."""
    try:
        if isinstance(as_of_date, datetime):
            as_of_date = as_of_date.isoformat()

        transactions = pd.read_sql(
            "SELECT * FROM transactions WHERE transaction_date <= :as_of_date",
            db_engine, params={"as_of_date": as_of_date}
        )

        if not transactions.empty:
            total_sales = transactions.loc[transactions["transaction_type"] == "sales", "price"].sum()
            total_purchases = transactions.loc[transactions["transaction_type"] == "stock_orders", "price"].sum()
            return float(total_sales - total_purchases)
        return 0.0
    except Exception as e:
        print(f"Error getting cash balance: {e}")
        return 0.0


def search_quote_history_db(search_terms: List[str], limit: int = 5) -> List[Dict]:
    """Search historical quotes matching search terms."""
    conditions = []
    params = {}

    for i, term in enumerate(search_terms):
        param_name = f"term_{i}"
        conditions.append(f"(LOWER(qr.response) LIKE :{param_name} OR LOWER(q.quote_explanation) LIKE :{param_name})")
        params[param_name] = f"%{term.lower()}%"

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    query = f"""
        SELECT qr.response AS original_request, q.total_amount, q.quote_explanation,
               q.job_type, q.order_size, q.event_type, q.order_date
        FROM quotes q
        JOIN quote_requests qr ON q.request_id = qr.id
        WHERE {where_clause}
        ORDER BY q.order_date DESC LIMIT {limit}
    """

    with db_engine.connect() as conn:
        result = conn.execute(text(query), params)
        return [dict(row._mapping) for row in result]


def generate_financial_report(as_of_date: Union[str, datetime]) -> Dict:
    """Generate a complete financial report for the company."""
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    cash = get_cash_balance_db(as_of_date)
    inventory_df = pd.read_sql("SELECT * FROM inventory", db_engine)
    inventory_value = 0.0
    inventory_summary = []

    for _, item in inventory_df.iterrows():
        stock_info = get_stock_level(item["item_name"], as_of_date)
        stock = stock_info["current_stock"].iloc[0]
        item_value = stock * item["unit_price"]
        inventory_value += item_value
        inventory_summary.append({
            "item_name": item["item_name"], "stock": stock,
            "unit_price": item["unit_price"], "value": item_value,
        })

    return {
        "as_of_date": as_of_date, "cash_balance": cash,
        "inventory_value": inventory_value, "total_assets": cash + inventory_value,
        "inventory_summary": inventory_summary,
    }


# =============================================================================
# TOOL IMPLEMENTATIONS
# =============================================================================

# -----------------------------------------------------------------------------
# Inventory Agent Tools
# -----------------------------------------------------------------------------

@tool
def check_inventory(item_name: str, as_of_date: str) -> str:
    """Check the current stock level for a specific paper product.

    Args:
        item_name: Exact name of the product (e.g., 'Glossy paper', 'Cardstock')
        as_of_date: Date to check inventory as of (ISO format: YYYY-MM-DD)

    Returns:
        A formatted string with item name, current stock, min threshold, and unit price.
    """
    # Find product in catalog for pricing and threshold
    product = None
    for p in paper_supplies:
        if p["item_name"].lower() == item_name.lower():
            product = p
            break

    if not product:
        similar = [p["item_name"] for p in paper_supplies
                   if item_name.lower() in p["item_name"].lower()]
        if similar:
            return f"ERROR: Item '{item_name}' not found.\nDid you mean: {', '.join(similar[:3])}?"
        return f"ERROR: Item '{item_name}' not found in catalog."

    # Get stock level from database
    stock_df = get_stock_level(item_name, as_of_date)
    current_stock = int(stock_df["current_stock"].iloc[0]) if not stock_df.empty else 0

    # Get min stock level from inventory table
    try:
        inv_df = pd.read_sql(
            "SELECT min_stock_level FROM inventory WHERE item_name = :item_name",
            db_engine, params={"item_name": product["item_name"]}
        )
        min_stock = int(inv_df["min_stock_level"].iloc[0]) if not inv_df.empty else 100
    except:
        min_stock = 100  # Default threshold

    # Determine status
    if current_stock == 0:
        status = "OUT OF STOCK"
    elif current_stock < min_stock:
        status = "LOW STOCK - REORDER RECOMMENDED"
    else:
        status = "IN STOCK"

    return f"""Item: {product['item_name']}
Current Stock: {current_stock} units
Minimum Threshold: {min_stock} units
Unit Price: ${product['unit_price']:.2f}
Status: {status}"""


@tool
def get_all_inventory(as_of_date: str) -> str:
    """Get a complete list of all items currently in stock.

    Args:
        as_of_date: Date to check inventory as of (ISO format: YYYY-MM-DD)

    Returns:
        A formatted table of all items with positive stock.
    """
    inventory = get_all_inventory_db(as_of_date)

    if not inventory:
        return f"No items in stock as of {as_of_date}."

    output = f"INVENTORY AS OF {as_of_date}\n"
    output += "=" * 50 + "\n"
    output += f"{'Item':<30} | {'Stock':>6} | {'Unit Price':>10}\n"
    output += "-" * 50 + "\n"

    for item_name, stock in sorted(inventory.items()):
        # Find price from catalog
        price = 0.0
        for p in paper_supplies:
            if p["item_name"] == item_name:
                price = p["unit_price"]
                break
        output += f"{item_name:<30} | {stock:>6} | ${price:>9.2f}\n"

    output += "-" * 50 + "\n"
    output += f"Total Items: {len(inventory)}"
    return output


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
    if quantity <= 0:
        return "ERROR: Quantity must be positive."

    # Find product in catalog
    product = None
    for p in paper_supplies:
        if p["item_name"].lower() == item_name.lower():
            product = p
            break

    if not product:
        return f"ERROR: Item '{item_name}' not found in catalog."

    # Calculate cost and check cash balance
    cost = quantity * product["unit_price"]
    cash_balance = get_cash_balance_db(order_date)

    if cost > cash_balance:
        return f"""ERROR: Insufficient funds for reorder.
Cost: ${cost:.2f}
Available Cash: ${cash_balance:.2f}"""

    # Create stock order transaction
    try:
        transaction_id = create_transaction(
            item_name=product["item_name"],
            transaction_type="stock_orders",
            quantity=quantity,
            price=cost,
            date=order_date
        )
    except Exception as e:
        return f"ERROR: Failed to create reorder transaction: {e}"

    # Calculate delivery date
    delivery_date = get_supplier_delivery_date(order_date, quantity)

    return f"""REORDER CONFIRMED
=================
Transaction ID: {transaction_id}
Item: {product['item_name']}
Quantity: {quantity} units
Cost: ${cost:.2f} (@ ${product['unit_price']:.2f}/unit)
Order Date: {order_date}
Estimated Delivery: {delivery_date}"""


# -----------------------------------------------------------------------------
# Quote Agent Tools
# -----------------------------------------------------------------------------

@tool
def get_item_price(item_name: str) -> str:
    """Get the unit price for a specific product.

    Args:
        item_name: Exact name of the product

    Returns:
        Item name and unit price, or error if not found.
    """
    # Search in product catalog
    for product in paper_supplies:
        if product["item_name"].lower() == item_name.lower():
            return f"""Item: {product['item_name']}
Unit Price: ${product['unit_price']:.2f} per unit
Category: {product['category']}"""

    # Fuzzy match - find similar items
    similar = [p["item_name"] for p in paper_supplies
               if item_name.lower() in p["item_name"].lower()]
    if similar:
        return f"ERROR: Item '{item_name}' not found.\nDid you mean: {', '.join(similar[:3])}?"
    return f"ERROR: Item '{item_name}' not found in catalog."


@tool
def search_quote_history(search_terms: str) -> str:
    """Search historical quotes for similar customer requests.

    Args:
        search_terms: Comma-separated keywords to search (e.g., 'glossy, conference, large')

    Returns:
        Up to 5 matching historical quotes with pricing and explanations.
    """
    terms = [t.strip() for t in search_terms.split(",") if t.strip()]
    if not terms:
        return "ERROR: No search terms provided."

    results = search_quote_history_db(terms, limit=5)

    if not results:
        return f"No historical quotes found matching: {', '.join(terms)}"

    output = "MATCHING HISTORICAL QUOTES\n==========================\n\n"
    for i, quote in enumerate(results, 1):
        total = quote.get("total_amount", 0)
        if total == -1:
            total_str = "Error in quote"
        else:
            total_str = f"${total:.2f}"
        output += f"""{i}. Request: "{quote.get('original_request', 'N/A')[:80]}..."
   Total: {total_str}
   Event: {quote.get('event_type', 'N/A')} | Size: {quote.get('order_size', 'N/A')}

"""
    output += f"Found {len(results)} matching quote(s)."
    return output


def calculate_bulk_discount(quantity: int) -> float:
    """Calculate bulk discount percentage based on quantity.

    Discount tiers:
    - < 100 units: 0%
    - 100-499 units: 5%
    - 500-999 units: 10%
    - 1000+ units: 15%
    """
    if quantity < 100:
        return 0.0
    elif quantity < 500:
        return 0.05
    elif quantity < 1000:
        return 0.10
    else:
        return 0.15


@tool
def calculate_quote(items_json: str) -> str:
    """Calculate a quote for multiple items with bulk discounts.

    Args:
        items_json: JSON string of items and quantities.
                    Accepted formats:
                    - Array: [{"item": "Glossy paper", "quantity": 500}, ...]
                    - Object: {"Glossy paper": 500, "Cardstock": 100}

    Returns:
        Detailed quote with itemized pricing, discounts, and total.
    """
    try:
        items = json.loads(items_json)
    except json.JSONDecodeError:
        return "ERROR: Invalid JSON format. Use [{\"item\": \"name\", \"quantity\": 100}, ...] or {\"item_name\": quantity, ...}"

    if not items:
        return "ERROR: No items provided in the quote request."

    # Normalize input: convert dict format to list format
    # Handles both {"item_name": quantity} and [{"item": "name", "quantity": 100}]
    if isinstance(items, dict):
        # Convert {"Glossy paper": 500, "Cardstock": 100} to [{"item": "Glossy paper", "quantity": 500}, ...]
        items = [{"item": k, "quantity": v} for k, v in items.items()]

    output = "QUOTE GENERATED\n===============\n\nItemized Pricing:\n-----------------\n"
    subtotal = 0.0
    total_discount = 0.0
    line_num = 0

    for item_data in items:
        item_name = item_data.get("item", "")
        quantity = item_data.get("quantity", 0)

        # Ensure quantity is an integer (LLMs sometimes pass strings)
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            quantity = 0

        if quantity <= 0:
            continue

        # Find product in catalog
        product = None
        for p in paper_supplies:
            if p["item_name"].lower() == item_name.lower():
                product = p
                break

        if not product:
            output += f"\n{item_name}: NOT FOUND IN CATALOG\n"
            continue

        line_num += 1
        unit_price = product["unit_price"]
        line_subtotal = quantity * unit_price
        discount_rate = calculate_bulk_discount(quantity)
        discount_amount = line_subtotal * discount_rate
        line_total = line_subtotal - discount_amount

        subtotal += line_subtotal
        total_discount += discount_amount

        output += f"\n{line_num}. {product['item_name']}\n"
        output += f"   Quantity: {quantity} units @ ${unit_price:.2f} each\n"
        output += f"   Subtotal: ${line_subtotal:.2f}\n"
        if discount_rate > 0:
            output += f"   Bulk Discount ({int(discount_rate*100)}%): -${discount_amount:.2f}\n"
        output += f"   Line Total: ${line_total:.2f}\n"

    final_total = subtotal - total_discount

    # Round to friendly number
    if final_total < 100:
        rounded_total = round(final_total / 5) * 5
    elif final_total < 500:
        rounded_total = round(final_total / 10) * 10
    else:
        rounded_total = round(final_total / 50) * 50

    output += f"""
-----------------
Subtotal: ${subtotal:.2f}
Total Discount: ${total_discount:.2f}
FINAL TOTAL: ${rounded_total:.2f}

Pricing Explanation:
Thank you for your order! """
    if total_discount > 0:
        output += f"We've applied bulk discounts totaling ${total_discount:.2f} due to your order quantities. "
    output += f"The final total has been rounded to ${rounded_total:.2f} for your convenience."

    return output


# -----------------------------------------------------------------------------
# Sales Agent Tools
# -----------------------------------------------------------------------------

@tool
def check_delivery_timeline(quantity: int, order_date: str) -> str:
    """Estimate delivery date based on order quantity.

    Args:
        quantity: Number of units being ordered
        order_date: Date order is placed (ISO format: YYYY-MM-DD)

    Returns:
        Estimated delivery date with lead time explanation.
    """
    if quantity <= 0:
        return "ERROR: Quantity must be positive."

    # Calculate lead time
    if quantity <= 10:
        lead_time = "Same day"
        days = 0
    elif quantity <= 100:
        lead_time = "1 business day"
        days = 1
    elif quantity <= 1000:
        lead_time = "4 business days"
        days = 4
    else:
        lead_time = "7 business days"
        days = 7

    delivery_date = get_supplier_delivery_date(order_date, quantity)

    return f"""DELIVERY ESTIMATE
=================
Order Quantity: {quantity} units
Order Date: {order_date}
Lead Time: {lead_time}
Estimated Delivery: {delivery_date}"""


def check_and_reorder_if_needed(item_name: str, quantity_needed: int, order_date: str) -> str:
    """Pre-fulfillment check: ensure stock is available, reorder if needed."""
    # Find product
    product = None
    for p in paper_supplies:
        if p["item_name"].lower() == item_name.lower():
            product = p
            break

    if not product:
        return None  # Let fulfill_order handle the error

    # Get current stock
    stock_df = get_stock_level(product["item_name"], order_date)
    current_stock = int(stock_df["current_stock"].iloc[0]) if not stock_df.empty else 0

    # Get min stock level
    try:
        inv_df = pd.read_sql(
            "SELECT min_stock_level FROM inventory WHERE item_name = :item_name",
            db_engine, params={"item_name": product["item_name"]}
        )
        min_stock = int(inv_df["min_stock_level"].iloc[0]) if not inv_df.empty else 100
    except:
        min_stock = 100

    # Check if reorder needed (stock after sale would fall below threshold)
    stock_after_sale = current_stock - quantity_needed

    if stock_after_sale < min_stock:
        # Calculate reorder quantity to reach 2x min threshold
        reorder_qty = (min_stock * 2) - stock_after_sale
        if reorder_qty > 0:
            # Trigger automatic reorder
            reorder_result = trigger_reorder(product["item_name"], reorder_qty, order_date)
            return f"AUTO-REORDER TRIGGERED:\n{reorder_result}"

    return None


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
    if quantity <= 0:
        return "ERROR: Quantity must be positive."
    if price < 0:
        return "ERROR: Price cannot be negative."

    # Find product in catalog
    product = None
    for p in paper_supplies:
        if p["item_name"].lower() == item_name.lower():
            product = p
            break

    if not product:
        similar = [p["item_name"] for p in paper_supplies
                   if item_name.lower() in p["item_name"].lower()]
        if similar:
            return f"ERROR: Item '{item_name}' not found.\nDid you mean: {', '.join(similar[:3])}?"
        return f"ERROR: Item '{item_name}' not found in catalog."

    # Pre-fulfillment inventory check and reorder if needed
    reorder_info = check_and_reorder_if_needed(product["item_name"], quantity, order_date)

    # Get current stock to verify availability
    stock_df = get_stock_level(product["item_name"], order_date)
    current_stock = int(stock_df["current_stock"].iloc[0]) if not stock_df.empty else 0

    # For items not in initial inventory, we can still fulfill (back-order from supplier)
    stock_warning = ""
    if current_stock < quantity and current_stock > 0:
        stock_warning = f"\nNote: Current stock ({current_stock}) is less than ordered ({quantity}). Back-ordering from supplier."

    # Create sales transaction
    try:
        transaction_id = create_transaction(
            item_name=product["item_name"],
            transaction_type="sales",
            quantity=quantity,
            price=price,
            date=order_date
        )
    except Exception as e:
        return f"ERROR: Failed to record sale: {e}"

    # Get updated balances
    new_cash = get_cash_balance_db(order_date)
    new_stock_df = get_stock_level(product["item_name"], order_date)
    new_stock = int(new_stock_df["current_stock"].iloc[0]) if not new_stock_df.empty else 0

    # Get delivery estimate
    delivery_date = get_supplier_delivery_date(order_date, quantity)

    output = f"""ORDER FULFILLED
===============
Transaction ID: {transaction_id}
Item: {product['item_name']}
Quantity: {quantity} units
Sale Price: ${price:.2f}
Date: {order_date}
Estimated Delivery: {delivery_date}

Updated Balances:
- Cash Balance: ${new_cash:.2f}
- {product['item_name']} Stock: {new_stock} units{stock_warning}

Thank you for your order!"""

    if reorder_info:
        output += f"\n\n{reorder_info}"

    return output


@tool
def get_cash_balance(as_of_date: str) -> str:
    """Get the current cash balance as of a specific date.

    Args:
        as_of_date: Date to check balance (ISO format: YYYY-MM-DD)

    Returns:
        Current cash balance with breakdown.
    """
    balance = get_cash_balance_db(as_of_date)

    # Get transaction summary
    try:
        transactions = pd.read_sql(
            "SELECT transaction_type, SUM(price) as total FROM transactions WHERE transaction_date <= :date GROUP BY transaction_type",
            db_engine, params={"date": as_of_date}
        )
        sales_total = transactions.loc[transactions["transaction_type"] == "sales", "total"].sum() if not transactions.empty else 0
        purchases_total = transactions.loc[transactions["transaction_type"] == "stock_orders", "total"].sum() if not transactions.empty else 0
    except:
        sales_total = balance
        purchases_total = 0

    return f"""CASH BALANCE AS OF {as_of_date}
=============================
Available Cash: ${balance:.2f}

Summary:
- Total Sales Revenue: ${sales_total:.2f}
- Total Stock Purchases: ${purchases_total:.2f}
- Net Balance: ${balance:.2f}"""


# =============================================================================
# AGENT DEFINITIONS
# =============================================================================

# Build product catalog string for agent prompts
PRODUCT_CATALOG = "\n".join([f"- {p['item_name']}: ${p['unit_price']:.2f}" for p in paper_supplies])

# -----------------------------------------------------------------------------
# Quote Agent (T015-T016)
# -----------------------------------------------------------------------------

QUOTE_AGENT_PROMPT = f"""You are the Quote Agent for Beaver's Choice Paper Company.

Your role is to generate accurate price quotes for customer requests.

PRODUCT CATALOG (use exact names):
{PRODUCT_CATALOG}

BULK DISCOUNT RULES:
- Less than 100 units: No discount
- 100-499 units: 5% discount
- 500-999 units: 10% discount
- 1000+ units: 15% discount

WORKFLOW - Complete these steps then STOP:
1. Identify items and quantities from the request
2. Map informal names to exact catalog names (e.g., "glossy" → "Glossy paper")
3. Call calculate_quote with the items as JSON
4. Return the quote result immediately - DO NOT call more tools after this

IMPORTANT: After calling calculate_quote, your task is DONE. Return the result.
"""

quote_agent = ToolCallingAgent(
    tools=[get_item_price, search_quote_history, calculate_quote],
    model=model,
    name="quote_agent",
    description="Generates price quotes with bulk discounts for paper supply orders.",
    prompt_templates=make_prompt_templates(QUOTE_AGENT_PROMPT),
    max_steps=5,  # Limit steps to prevent infinite loops
)

# -----------------------------------------------------------------------------
# Inventory Agent (T022-T023)
# -----------------------------------------------------------------------------

INVENTORY_AGENT_PROMPT = f"""You are the Inventory Agent for Beaver's Choice Paper Company.

Your role is to check stock levels and trigger reorders when needed.

PRODUCT CATALOG (use exact names):
{PRODUCT_CATALOG}

WORKFLOW - Complete the task then STOP:
1. If asked about specific item(s): Call check_inventory for each item
2. If asked for full inventory: Call get_all_inventory once
3. If stock is LOW and reorder needed: Call trigger_reorder
4. Return the results immediately - DO NOT call more tools after this

REORDER RULES:
- Only reorder if stock is below minimum threshold
- Reorder enough to reach 2x minimum threshold

IMPORTANT: After completing the check (1-2 tool calls max), return results immediately.
"""

inventory_agent = ToolCallingAgent(
    tools=[check_inventory, get_all_inventory, trigger_reorder],
    model=model,
    name="inventory_agent",
    description="Manages inventory levels and triggers automatic reorders when stock is low.",
    prompt_templates=make_prompt_templates(INVENTORY_AGENT_PROMPT),
    max_steps=5,  # Limit steps to prevent infinite loops
)

# -----------------------------------------------------------------------------
# Sales Agent (T030-T031)
# -----------------------------------------------------------------------------

SALES_AGENT_PROMPT = f"""You are the Sales Agent for Beaver's Choice Paper Company.

Your role is to process orders and provide delivery estimates.

PRODUCT CATALOG (use exact names):
{PRODUCT_CATALOG}

DELIVERY LEAD TIMES:
- ≤10 units: Same day
- 11-100 units: 1 business day
- 101-1000 units: 4 business days
- >1000 units: 7 business days

WORKFLOW - Complete the task then STOP:
1. If processing an order: Call fulfill_order with item, quantity, price, date
2. If checking delivery: Call check_delivery_timeline
3. Return the results immediately - DO NOT call more tools after this

IMPORTANT: Most tasks need only ONE tool call. After calling fulfill_order or check_delivery_timeline, return the result immediately.
"""

sales_agent = ToolCallingAgent(
    tools=[check_delivery_timeline, fulfill_order, get_cash_balance],
    model=model,
    name="sales_agent",
    description="Processes sales orders, handles fulfillment, and provides delivery estimates.",
    prompt_templates=make_prompt_templates(SALES_AGENT_PROMPT),
    max_steps=5,  # Limit steps to prevent infinite loops
)

# -----------------------------------------------------------------------------
# Orchestrator Agent (T034-T040)
# -----------------------------------------------------------------------------

ORCHESTRATOR_PROMPT = """You are the Orchestrator for Beaver's Choice Paper Company.

Route customer requests to specialist agents, then return the result.

AGENTS:
- quote_agent(task) - For price quotes and pricing requests
- inventory_agent(task) - For stock checks
- sales_agent(task) - For order processing

IMPORTANT: You MUST write Python code wrapped in <code> and </code> tags.

EXAMPLE FORMAT (copy this structure exactly):
<code>
result = quote_agent("Generate quote for 200 glossy paper")
final_answer(result)
</code>

ROUTING:
- Price/quote requests → quote_agent
- Stock/inventory checks → inventory_agent
- Order fulfillment → sales_agent

RULES:
1. Always start with <code> and end with </code>
2. Call ONE agent, then final_answer(result)
3. No extra text outside the code tags
"""

orchestrator = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[inventory_agent, quote_agent, sales_agent],
    prompt_templates=make_prompt_templates(ORCHESTRATOR_PROMPT),
    max_steps=10,  # Reduced - sub-agents now have their own limits
)


# =============================================================================
# TEST HARNESS
# =============================================================================

def run_test_scenarios(max_requests: int = None):
    """Process test scenarios from quote_requests_sample.csv.

    Args:
        max_requests: Optional limit on number of requests to process (for testing)
    """
    print("=" * 60)
    print("BEAVER'S CHOICE PAPER COMPANY - MULTI-AGENT SYSTEM")
    print("=" * 60)
    print("\nInitializing Database...")
    init_database(db_engine)
    print("Database initialized successfully.\n")

    try:
        sample_path = "project-starter-ref-code/quote_requests_sample.csv"
        quote_requests_sample = pd.read_csv(sample_path)
        quote_requests_sample["request_date"] = pd.to_datetime(
            quote_requests_sample["request_date"], format="%m/%d/%y", errors="coerce"
        )
        quote_requests_sample.dropna(subset=["request_date"], inplace=True)
        quote_requests_sample = quote_requests_sample.sort_values("request_date")

        # Optionally limit number of requests for testing
        if max_requests:
            quote_requests_sample = quote_requests_sample.head(max_requests)
            print(f"Processing {max_requests} requests (limited mode)\n")
        else:
            print(f"Processing {len(quote_requests_sample)} requests\n")

    except Exception as e:
        print(f"FATAL: Error loading test data: {e}")
        return

    # Get initial state
    initial_date = quote_requests_sample["request_date"].min().strftime("%Y-%m-%d")
    report = generate_financial_report(initial_date)
    current_cash = report["cash_balance"]
    current_inventory = report["inventory_value"]

    results = []
    for idx, row in quote_requests_sample.iterrows():
        request_date = row["request_date"].strftime("%Y-%m-%d")

        print(f"\n=== Request {idx+1} ===")
        print(f"Context: {row['job']} organizing {row['event']}")
        print(f"Request Date: {request_date}")
        print(f"Cash Balance: ${current_cash:.2f}")
        print(f"Inventory Value: ${current_inventory:.2f}")

        request_with_date = f"{row['request']} (Date of request: {request_date})"

        # Call orchestrator agent
        try:
            response = orchestrator.run(request_with_date)
        except Exception as e:
            response = f"Error processing request: {e}"

        report = generate_financial_report(request_date)
        current_cash = report["cash_balance"]
        current_inventory = report["inventory_value"]

        print(f"Response: {response}")
        print(f"Updated Cash: ${current_cash:.2f}")
        print(f"Updated Inventory: ${current_inventory:.2f}")

        results.append({
            "request_id": idx + 1, "request_date": request_date,
            "cash_balance": current_cash, "inventory_value": current_inventory,
            "response": response,
        })

        time.sleep(1)

    # Final report
    final_date = quote_requests_sample["request_date"].max().strftime("%Y-%m-%d")
    final_report = generate_financial_report(final_date)
    print("\n===== FINAL FINANCIAL REPORT =====")
    print(f"Final Cash: ${final_report['cash_balance']:.2f}")
    print(f"Final Inventory: ${final_report['inventory_value']:.2f}")

    pd.DataFrame(results).to_csv("test_results.csv", index=False)
    return results


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import sys

    # Allow limiting requests via command line: python beaver_agents.py 3
    max_requests = None
    if len(sys.argv) > 1:
        try:
            max_requests = int(sys.argv[1])
            print(f"Running with limit: {max_requests} requests")
        except ValueError:
            pass

    results = run_test_scenarios(max_requests=max_requests)
