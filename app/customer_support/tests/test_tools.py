"""Tests for customer support tools — knowledge base and refund processing.

These are pure-function tests (no external dependencies).
"""

import json

import pytest

from tools.knowledge_base import FAQ_DATABASE, search_faq
from tools.refund_tools import ORDERS_DATABASE, lookup_order, process_refund


# ---------------------------------------------------------------------------
# search_faq
# ---------------------------------------------------------------------------

class TestSearchFaq:
    """Tests for the FAQ knowledge base search tool."""

    def test_exact_topic_match(self):
        result = search_faq("return policy")
        assert "Return Policy" in result
        assert "30 days" in result

    def test_partial_keyword_match(self):
        result = search_faq("how long does shipping take?")
        assert "shipping" in result.lower()
        assert "5-7 business days" in result

    def test_payment_query(self):
        result = search_faq("what payment methods do you accept?")
        assert "Visa" in result

    def test_warranty_query(self):
        result = search_faq("warranty information")
        assert "1-year" in result

    def test_business_hours_query(self):
        result = search_faq("business hours")
        assert "Monday" in result

    def test_no_match_returns_fallback(self):
        result = search_faq("quantum physics")
        assert "No matching FAQ entries found" in result

    def test_case_insensitive(self):
        result = search_faq("SHIPPING")
        assert "shipping" in result.lower()

    def test_multiple_matches(self):
        """A query touching multiple topics should return all matches."""
        result = search_faq("return shipping")
        assert "Return Policy" in result
        assert "Shipping" in result

    def test_all_topics_reachable(self):
        """Every FAQ topic must be searchable by at least one of its keywords."""
        for topic in FAQ_DATABASE:
            first_keyword = topic.split()[0]
            result = search_faq(first_keyword)
            assert "No matching FAQ entries found" not in result, (
                f"Topic '{topic}' unreachable with keyword '{first_keyword}'"
            )


# ---------------------------------------------------------------------------
# lookup_order
# ---------------------------------------------------------------------------

class TestLookupOrder:
    """Tests for the order lookup tool."""

    def test_existing_order(self):
        result = json.loads(lookup_order("12345"))
        assert result["order_id"] == "12345"
        assert result["item"] == "Wireless Headphones"
        assert result["amount"] == 129.99
        assert result["refund_eligible"] is True

    def test_in_transit_order(self):
        result = json.loads(lookup_order("67890"))
        assert result["status"] == "in_transit"
        assert result["refund_eligible"] is False

    def test_nonexistent_order(self):
        result = json.loads(lookup_order("99999"))
        assert "error" in result
        assert "not found" in result["error"]

    def test_all_orders_in_database(self):
        """All orders in the database should be retrievable."""
        for order_id in ORDERS_DATABASE:
            result = json.loads(lookup_order(order_id))
            assert "error" not in result
            assert result["order_id"] == order_id


# ---------------------------------------------------------------------------
# process_refund
# ---------------------------------------------------------------------------

class TestProcessRefund:
    """Tests for the refund processing tool."""

    def test_successful_full_refund(self):
        result = json.loads(process_refund("12345", 129.99))
        assert result["status"] == "refund_processed"
        assert result["refund_amount"] == 129.99

    def test_successful_partial_refund(self):
        result = json.loads(process_refund("12345", 50.00))
        assert result["status"] == "refund_processed"
        assert result["refund_amount"] == 50.00

    def test_refund_exceeds_order_total(self):
        result = json.loads(process_refund("12345", 999.99))
        assert "error" in result
        assert "exceeds" in result["error"]

    def test_zero_amount_rejected(self):
        result = json.loads(process_refund("12345", 0))
        assert "error" in result
        assert "greater than zero" in result["error"]

    def test_negative_amount_rejected(self):
        result = json.loads(process_refund("12345", -10.0))
        assert "error" in result
        assert "greater than zero" in result["error"]

    def test_nonexistent_order_refund(self):
        result = json.loads(process_refund("99999", 10.0))
        assert "error" in result
        assert "not found" in result["error"]

    def test_all_eligible_orders_refundable(self):
        """Every refund-eligible order should process successfully at its full amount."""
        for order_id, order in ORDERS_DATABASE.items():
            if order["refund_eligible"]:
                result = json.loads(process_refund(order_id, order["amount"]))
                assert result["status"] == "refund_processed", (
                    f"Order {order_id} should be refundable"
                )
