"""
Unit tests for Data Validation Engine.
"""

import pytest
import pandas as pd
from src.data_validation import (
    validate_financial_data,
    validate_operational_data,
    validate_kpi_definitions
)

def test_validate_financial_data_pass():
    df = pd.DataFrame([
        {
            "date": "2025-01-01",
            "business_unit": "Enterprise Solutions",
            "region": "North America",
            "product_category": "Software",
            "revenue": 100000.0,
            "cost_of_goods_sold": 40000.0,
            "operating_expenses": 30000.0,
            "gross_profit": 60000.0,
            "operating_profit": 30000.0,
            "cash_flow": 25000.0,
            "customer_count": 50,
            "orders_count": 80
        }
    ])
    report = validate_financial_data(df)
    assert report.status == "PASS"
    assert len(report.errors) == 0

def test_validate_financial_data_math_mismatch():
    # Intentionally broken identity: Gross profit != Rev - COGS
    df = pd.DataFrame([
        {
            "date": "2025-01-01",
            "business_unit": "Enterprise Solutions",
            "region": "North America",
            "product_category": "Software",
            "revenue": 100000.0,
            "cost_of_goods_sold": 40000.0,
            "operating_expenses": 30000.0,
            "gross_profit": 99999.0, # Error!
            "operating_profit": 30000.0,
            "cash_flow": 25000.0,
            "customer_count": 50,
            "orders_count": 80
        }
    ])
    report = validate_financial_data(df)
    assert report.status == "WARNING"
    assert any("Gross Profit mismatch" in w for w in report.warnings)

def test_validate_financial_data_missing_column():
    df = pd.DataFrame([{"date": "2025-01-01"}])
    report = validate_financial_data(df)
    assert report.status == "FAIL"
    assert any("Missing required columns" in e for e in report.errors)
