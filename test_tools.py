"""
Unit Tests for Beaver's Choice Paper Company Tools
===================================================

Tests tool functions in isolation to validate edge cases before
running full agent integration tests.

Run with: python -m pytest test_tools.py -v
Or simply: python test_tools.py
"""

import json
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

# Import the tool functions and helpers from beaver_agents
from beaver_agents import (
    # Tool functions (decorated with @tool)
    check_inventory,
    get_all_inventory,
    trigger_reorder,
    get_item_price,
    search_quote_history,
    calculate_quote,
    check_delivery_timeline,
    fulfill_order,
    get_cash_balance,
    # Helper functions
    calculate_bulk_discount,
    paper_supplies,
    init_database,
    db_engine,
)


class TestCalculateQuote(unittest.TestCase):
    """Tests for the calculate_quote tool - validates input format handling."""

    def test_list_format_single_item(self):
        """Test with array format: [{"item": "name", "quantity": 100}]"""
        items_json = json.dumps([{"item": "Glossy paper", "quantity": 100}])
        result = calculate_quote(items_json)
        self.assertIn("QUOTE GENERATED", result)
        self.assertIn("Glossy paper", result)
        self.assertNotIn("ERROR", result)

    def test_list_format_multiple_items(self):
        """Test with array format containing multiple items."""
        items_json = json.dumps([
            {"item": "Glossy paper", "quantity": 200},
            {"item": "Cardstock", "quantity": 100},
            {"item": "Colored paper", "quantity": 100}
        ])
        result = calculate_quote(items_json)
        self.assertIn("QUOTE GENERATED", result)
        self.assertIn("Glossy paper", result)
        self.assertIn("Cardstock", result)
        self.assertNotIn("ERROR", result)

    def test_dict_format_single_item(self):
        """Test with object format: {"item_name": quantity}"""
        items_json = json.dumps({"Glossy paper": 100})
        result = calculate_quote(items_json)
        self.assertIn("QUOTE GENERATED", result)
        self.assertIn("Glossy paper", result)
        self.assertNotIn("ERROR", result)

    def test_dict_format_multiple_items(self):
        """Test with object format containing multiple items (LLM common pattern)."""
        items_json = json.dumps({
            "A4 glossy paper": 200,
            "heavy cardstock": 100,
            "colored paper": 100
        })
        result = calculate_quote(items_json)
        self.assertIn("QUOTE GENERATED", result)
        # Note: "A4 glossy paper" won't match exactly, but should not crash
        self.assertNotIn("AttributeError", result)

    def test_invalid_json(self):
        """Test with invalid JSON string."""
        result = calculate_quote("not valid json {")
        self.assertIn("ERROR", result)
        self.assertIn("Invalid JSON", result)

    def test_empty_items(self):
        """Test with empty items list."""
        result = calculate_quote("[]")
        self.assertIn("ERROR", result)
        self.assertIn("No items", result)

    def test_empty_dict(self):
        """Test with empty object."""
        result = calculate_quote("{}")
        self.assertIn("ERROR", result)
        self.assertIn("No items", result)

    def test_zero_quantity(self):
        """Test items with zero quantity are skipped."""
        items_json = json.dumps([{"item": "Glossy paper", "quantity": 0}])
        result = calculate_quote(items_json)
        # Should generate quote but with no line items
        self.assertIn("QUOTE GENERATED", result)

    def test_item_not_in_catalog(self):
        """Test with item name not in catalog."""
        items_json = json.dumps([{"item": "Unicorn Paper", "quantity": 100}])
        result = calculate_quote(items_json)
        self.assertIn("NOT FOUND IN CATALOG", result)


class TestCalculateBulkDiscount(unittest.TestCase):
    """Tests for the bulk discount calculation logic."""

    def test_no_discount_under_100(self):
        """No discount for quantities under 100."""
        self.assertEqual(calculate_bulk_discount(50), 0.0)
        self.assertEqual(calculate_bulk_discount(99), 0.0)

    def test_5_percent_discount_100_to_499(self):
        """5% discount for 100-499 units."""
        self.assertEqual(calculate_bulk_discount(100), 0.05)
        self.assertEqual(calculate_bulk_discount(499), 0.05)

    def test_10_percent_discount_500_to_999(self):
        """10% discount for 500-999 units."""
        self.assertEqual(calculate_bulk_discount(500), 0.10)
        self.assertEqual(calculate_bulk_discount(999), 0.10)

    def test_15_percent_discount_1000_plus(self):
        """15% discount for 1000+ units."""
        self.assertEqual(calculate_bulk_discount(1000), 0.15)
        self.assertEqual(calculate_bulk_discount(5000), 0.15)


class TestGetItemPrice(unittest.TestCase):
    """Tests for the get_item_price tool."""

    def test_exact_match(self):
        """Test with exact item name."""
        result = get_item_price("Glossy paper")
        self.assertIn("Item: Glossy paper", result)
        self.assertIn("Unit Price:", result)
        self.assertNotIn("ERROR", result)

    def test_case_insensitive(self):
        """Test case insensitivity."""
        result = get_item_price("GLOSSY PAPER")
        self.assertIn("Glossy paper", result)
        self.assertNotIn("ERROR", result)

    def test_item_not_found_with_suggestion(self):
        """Test item not found suggests similar items."""
        result = get_item_price("glossy")  # Partial match
        self.assertIn("ERROR", result)
        self.assertIn("Did you mean", result)

    def test_item_completely_not_found(self):
        """Test completely unknown item."""
        result = get_item_price("Unicorn Glitter Supreme")
        self.assertIn("ERROR", result)
        self.assertIn("not found", result)


class TestCheckDeliveryTimeline(unittest.TestCase):
    """Tests for the check_delivery_timeline tool."""

    def test_same_day_delivery(self):
        """Test same day delivery for <= 10 units."""
        result = check_delivery_timeline(5, "2025-04-01")
        self.assertIn("Same day", result)

    def test_one_day_delivery(self):
        """Test 1 day delivery for 11-100 units."""
        result = check_delivery_timeline(50, "2025-04-01")
        self.assertIn("1 business day", result)

    def test_four_day_delivery(self):
        """Test 4 day delivery for 101-1000 units."""
        result = check_delivery_timeline(500, "2025-04-01")
        self.assertIn("4 business days", result)

    def test_seven_day_delivery(self):
        """Test 7 day delivery for > 1000 units."""
        result = check_delivery_timeline(2000, "2025-04-01")
        self.assertIn("7 business days", result)

    def test_invalid_quantity(self):
        """Test with invalid (zero or negative) quantity."""
        result = check_delivery_timeline(0, "2025-04-01")
        self.assertIn("ERROR", result)
        result = check_delivery_timeline(-5, "2025-04-01")
        self.assertIn("ERROR", result)


class TestPaperSuppliesCatalog(unittest.TestCase):
    """Tests for the product catalog data structure."""

    def test_catalog_has_items(self):
        """Ensure catalog is populated."""
        self.assertGreater(len(paper_supplies), 40)  # Should have 44 items

    def test_catalog_item_structure(self):
        """Ensure each item has required fields."""
        for item in paper_supplies:
            self.assertIn("item_name", item)
            self.assertIn("category", item)
            self.assertIn("unit_price", item)
            self.assertIsInstance(item["unit_price"], (int, float))
            self.assertGreater(item["unit_price"], 0)

    def test_catalog_categories(self):
        """Ensure expected categories exist."""
        categories = set(item["category"] for item in paper_supplies)
        self.assertIn("paper", categories)
        self.assertIn("product", categories)


class TestDatabaseIntegration(unittest.TestCase):
    """Integration tests that require database initialization."""

    @classmethod
    def setUpClass(cls):
        """Initialize database before all tests."""
        init_database(db_engine)

    def test_check_inventory_known_item(self):
        """Test checking inventory for a seeded item."""
        # This depends on the random seed, but Cardstock should be in catalog
        result = check_inventory("Cardstock", "2025-04-01")
        # Should return item info or not found (depending on seed)
        self.assertIn("Item:", result)

    def test_get_all_inventory_returns_data(self):
        """Test get_all_inventory returns items."""
        result = get_all_inventory("2025-04-01")
        self.assertIn("INVENTORY AS OF", result)

    def test_get_cash_balance_initial(self):
        """Test initial cash balance is seeded."""
        result = get_cash_balance("2025-01-01")
        self.assertIn("CASH BALANCE", result)
        self.assertIn("$", result)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases that might cause runtime errors."""

    def test_calculate_quote_with_string_quantity(self):
        """Test calculate_quote handles string quantities gracefully."""
        # This simulates an LLM passing incorrect types
        items_json = json.dumps([{"item": "Glossy paper", "quantity": "100"}])
        result = calculate_quote(items_json)
        # Should not crash, may produce an error or skip the item
        self.assertNotIn("AttributeError", result)
        self.assertNotIn("TypeError", result)

    def test_calculate_quote_with_mixed_format(self):
        """Test with edge case JSON that might confuse the parser."""
        # Mixed array with some malformed entries
        items_json = json.dumps([
            {"item": "Glossy paper", "quantity": 100},
            {"item": "", "quantity": 50},  # Empty item name
            {"item": "Cardstock"},  # Missing quantity
        ])
        result = calculate_quote(items_json)
        self.assertNotIn("KeyError", result)
        self.assertNotIn("AttributeError", result)


def run_tests():
    """Run all tests and print summary."""
    print("=" * 60)
    print("Running Beaver's Choice Paper Company Tool Tests")
    print("=" * 60)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCalculateQuote))
    suite.addTests(loader.loadTestsFromTestCase(TestCalculateBulkDiscount))
    suite.addTests(loader.loadTestsFromTestCase(TestGetItemPrice))
    suite.addTests(loader.loadTestsFromTestCase(TestCheckDeliveryTimeline))
    suite.addTests(loader.loadTestsFromTestCase(TestPaperSuppliesCatalog))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)

    return result


if __name__ == "__main__":
    run_tests()
