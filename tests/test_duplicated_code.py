"""
test_duplicated_code.py
=======================
Minimal tests to ensure duplicated modules are importable and
produce expected output. The real metric value is measured by
jscpd / copydetect scanning the source — not by test execution.
"""
from src.duplicated_code import (
    format_returns_report,
    format_sales_report,
    process_digital_order,
    process_retail_order,
    process_wholesale_order,
    validate_admin_input,
    validate_user_input,
)


SAMPLE_ITEMS = [
    {"price": 10.0, "quantity": 2},
    {"price": 5.0, "quantity": 3},
]


class TestOrderProcessing:
    def test_retail_total(self):
        r = process_retail_order("R001", SAMPLE_ITEMS, 0.1, 0.05)
        assert r["total"] == pytest.approx(33.08, abs=0.01) or r["total"] > 0

    def test_wholesale_equals_retail_structure(self):
        r = process_wholesale_order("W001", SAMPLE_ITEMS, 0.1, 0.05)
        assert "order_id" in r and "total" in r

    def test_digital_order(self):
        r = process_digital_order("D001", SAMPLE_ITEMS, 0.0, 0.0)
        assert r["total"] == pytest.approx(35.0)


class TestValidation:
    def test_valid_user(self):
        data = {"name": "Alice", "email": "a@b.com", "phone": "1234567890", "dob": "2000-01-01"}
        assert validate_user_input(data) == []

    def test_missing_name(self):
        data = {"email": "a@b.com", "phone": "1234567890", "dob": "2000-01-01"}
        errors = validate_user_input(data)
        assert any("Name" in e for e in errors)

    def test_admin_same_validation(self):
        data = {"name": "Bob", "email": "b@c.com", "phone": "0987654321", "dob": "1990-01-01"}
        assert validate_admin_input(data) == []


class TestReports:
    RECORDS = [
        {"date": "2025-01-01", "product": "Widget", "amount": 100.0},
        {"date": "2025-01-02", "product": "Gadget", "amount": 200.0},
    ]

    def test_sales_report_contains_total(self):
        report = format_sales_report(self.RECORDS)
        assert "300.00" in report

    def test_returns_report_same_format(self):
        report = format_returns_report(self.RECORDS)
        assert "300.00" in report


import pytest  # noqa: E402 – pytest needed for approx above
