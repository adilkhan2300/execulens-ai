"""
Unit tests for Scenario Engine and What-if Simulation.
"""

import pytest
from src.scenario_engine import simulate_what_if_scenario, generate_scenario_matrix_comparison

def test_simulate_what_if_scenario():
    base = {
        "revenue": 1_000_000.0,
        "orders_count": 1000,
        "average_order_value": 1000.0,
        "cogs": 500_000.0,
        "operating_expenses": 300_000.0,
        "operating_profit": 200_000.0,
        "operating_margin_pct": 20.0,
        "fulfillment_cost_per_order": 15.0,
    }

    # +10% conversion rate -> +10% order volume
    res = simulate_what_if_scenario(base, conversion_rate_delta_pct=10.0)
    assert res["simulated_orders"] == 1100
    assert res["simulated_revenue"] == 1_100_000.0
    assert res["revenue_delta"] == 100_000.0
    assert res["simulated_operating_profit"] > base["operating_profit"]

def test_generate_scenario_matrix_comparison():
    base = {
        "revenue": 2_000_000.0,
        "orders_count": 2000,
        "average_order_value": 1000.0,
        "cogs": 900_000.0,
        "operating_expenses": 600_000.0,
        "operating_profit": 500_000.0,
        "operating_margin_pct": 25.0,
        "fulfillment_cost_per_order": 18.0,
    }

    scen_df = generate_scenario_matrix_comparison(base)
    assert len(scen_df) == 5
    # BAU should have zero profit delta
    bau_row = scen_df[scen_df["Scenario Name"].str.contains("BAU")].iloc[0]
    assert bau_row["Profit Delta"] == 0.0
