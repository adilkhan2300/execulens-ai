"""
Unit tests for KPI Engine: status evaluation, scorecard, growth, and composite score.
"""

import pytest
import pandas as pd
from src.kpi_engine import evaluate_kpi_status, compute_executive_scorecard

def test_evaluate_kpi_status_higher_is_better():
    # Healthy
    status, sent, pct = evaluate_kpi_status(100, 90, "higher_is_better", warning_threshold=80, critical_threshold=70)
    assert status == "Healthy"
    assert sent == "Favorable"
    assert pct > 0

    # Warning
    status, sent, pct = evaluate_kpi_status(75, 90, "higher_is_better", warning_threshold=80, critical_threshold=70)
    assert status == "Warning"
    assert sent == "Unfavorable"

    # Critical
    status, sent, pct = evaluate_kpi_status(65, 90, "higher_is_better", warning_threshold=80, critical_threshold=70)
    assert status == "Critical"
    assert sent == "Unfavorable"

def test_evaluate_kpi_status_lower_is_better():
    # Healthy (lower than target)
    status, sent, pct = evaluate_kpi_status(10, 15, "lower_is_better", warning_threshold=20, critical_threshold=25)
    assert status == "Healthy"
    assert sent == "Favorable"

    # Critical (above critical threshold)
    status, sent, pct = evaluate_kpi_status(28, 15, "lower_is_better", warning_threshold=20, critical_threshold=25)
    assert status == "Critical"
    assert sent == "Unfavorable"

def test_compute_executive_scorecard():
    df = pd.DataFrame([
        {
            "date": "2025-01-01",
            "revenue": 1000000.0,
            "cost_of_goods_sold": 500000.0,
            "operating_expenses": 300000.0,
            "gross_profit": 500000.0,
            "operating_profit": 200000.0,
            "cash_flow": 180000.0,
            "budget_revenue": 950000.0,
            "budget_operating_profit": 190000.0,
        },
        {
            "date": "2025-02-01",
            "revenue": 1100000.0,
            "cost_of_goods_sold": 550000.0,
            "operating_expenses": 320000.0,
            "gross_profit": 550000.0,
            "operating_profit": 230000.0,
            "cash_flow": 210000.0,
            "budget_revenue": 1000000.0,
            "budget_operating_profit": 200000.0,
        }
    ])

    scorecard = compute_executive_scorecard(df)
    assert scorecard["current_period"] == "2025-02-01"
    assert scorecard["previous_period"] == "2025-01-01"
    assert scorecard["revenue"]["value"] == 1100000.0
    assert scorecard["revenue"]["change_pct"] == 10.0
    assert scorecard["revenue"]["favorable"] is True
    assert scorecard["operating_profit"]["value"] == 230000.0
    assert scorecard["operating_profit"]["change_pct"] == 15.0
    assert scorecard["operating_margin"]["value"] == pytest.approx(20.91, 0.1)
    assert 0 <= scorecard["performance_score"] <= 100
