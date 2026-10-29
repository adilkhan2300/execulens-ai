"""
Unit tests for financial analysis and variance decomposition.
"""

import pytest
import pandas as pd
from src.financial_analysis import decompose_profit_variance, analyze_budget_variances

def test_decompose_profit_variance():
    df = pd.DataFrame([
        {
            "date": "2025-01-01",
            "business_unit": "Enterprise Solutions",
            "region": "North America",
            "revenue": 100000.0,
            "cost_of_goods_sold": 40000.0,
            "operating_expenses": 30000.0,
            "operating_profit": 30000.0,
            "orders_count": 100
        },
        {
            "date": "2025-02-01",
            "business_unit": "Enterprise Solutions",
            "region": "North America",
            "revenue": 120000.0,
            "cost_of_goods_sold": 55000.0,
            "operating_expenses": 35000.0,
            "operating_profit": 30000.0,
            "orders_count": 115
        }
    ])

    res = decompose_profit_variance(df, "2025-01-01", "2025-02-01")
    assert res["base_profit"] == 30000.0
    assert res["final_profit"] == 30000.0
    assert res["total_profit_change"] == 0.0
    assert res["revenue_variance"] == 20000.0
    assert res["cogs_variance"] == 15000.0
    assert res["opex_variance"] == 5000.0
    # Identity: Rev Variance - COGS Variance - OpEx Variance = Profit Variance
    assert res["revenue_variance"] - res["cogs_variance"] - res["opex_variance"] == pytest.approx(res["total_profit_change"], 0.01)

def test_analyze_budget_variances():
    df = pd.DataFrame([
        {
            "date": "2025-01-01",
            "business_unit": "Enterprise Solutions",
            "region": "North America",
            "revenue": 100000.0,
            "budget_revenue": 90000.0,
            "operating_profit": 25000.0,
            "budget_operating_profit": 20000.0
        }
    ])
    res = analyze_budget_variances(df, "2025-01-01")
    assert len(res) == 1
    assert res["rev_variance"].iloc[0] == 10000.0
    assert res["profit_variance"].iloc[0] == 5000.0
    assert res["profit_variance_pct"].iloc[0] == 25.0
