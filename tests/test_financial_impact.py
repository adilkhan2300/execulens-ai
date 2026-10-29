"""
Unit tests for financial impact modeling calculations.
"""

import pytest
from src.financial_impact import (
    model_conversion_rate_impact,
    model_cac_impact,
    model_stockout_impact,
    model_turnover_cost_impact,
    model_fulfillment_cost_impact
)

def test_model_conversion_rate_impact():
    res = model_conversion_rate_impact(base_orders=1000, avg_order_value=2000.0, current_rate=4.0, target_rate=5.0)
    # (4 - 5) / 5 = -0.20 -> -200 orders * 2000 = -400,000
    assert res["base_financial_impact"] == -400000.0
    assert res["low_scenario"] < res["base_financial_impact"]
    assert res["high_scenario"] > res["base_financial_impact"]

def test_model_cac_impact():
    res = model_cac_impact(new_customers_acquired=100, current_cac=1500.0, target_cac=1200.0)
    # Delta CAC = 300 * 100 = 30,000 cost -> -30,000 profit impact
    assert res["base_financial_impact"] == -30000.0

def test_model_stockout_impact():
    res = model_stockout_impact(total_orders_demand=1000, avg_order_value=1000.0, stockout_rate_pct=3.5, target_stockout_pct=1.5)
    assert res["base_financial_impact"] < 0

def test_model_turnover_cost_impact():
    res = model_turnover_cost_impact(total_headcount=100, voluntary_turnover_pct=18.5, target_turnover_pct=8.5, avg_annual_salary=100000.0)
    # 10 excess departures * (100k * 0.5) = -500,000
    assert res["base_financial_impact"] == -500000.0
