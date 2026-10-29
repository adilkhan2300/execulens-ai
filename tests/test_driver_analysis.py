"""
Unit tests for Driver Analysis and Lag screening.
"""

import pytest
import numpy as np
import pandas as pd
from src.driver_analysis import analyze_kpi_correlations, run_multivariable_regression
from src.lag_analysis import compute_lagged_correlations

def test_analyze_kpi_correlations():
    # Construct synthetic relationship: Revenue = 1000 * KPI_A + noise
    np.random.seed(42)
    n = 20
    kpi_a = np.linspace(10, 50, n)
    rev = 1000 * kpi_a + np.random.normal(0, 500, n)
    
    df = pd.DataFrame({
        "revenue": rev,
        "KPI_A": kpi_a,
    })

    defs = {
        "KPI_A": {
            "department": "Sales",
            "target_value": 30.0,
            "direction": "higher_is_better",
            "linked_financial_outcome": "revenue"
        }
    }

    res = analyze_kpi_correlations(df, "revenue", ["KPI_A"], defs)
    assert len(res) == 1
    assert res["pearson_r"].iloc[0] > 0.8
    assert res["driver_score"].iloc[0] > 60
    assert res["direction_of_association"].iloc[0] == "Positive"

def test_run_multivariable_regression():
    np.random.seed(42)
    n = 30
    x1 = np.random.normal(10, 2, n)
    x2 = np.random.normal(5, 1, n)
    y = 50 + 3.0 * x1 - 2.0 * x2 + np.random.normal(0, 0.5, n)

    df = pd.DataFrame({"y": y, "X1": x1, "X2": x2})
    res = run_multivariable_regression(df, "y", ["X1", "X2"])
    
    assert res["success"] is True
    assert res["r_squared"] > 0.85
    coefs = {c["feature"]: c["coefficient"] for c in res["coefficients"]}
    assert coefs["X1"] == pytest.approx(3.0, abs=0.5)
    assert coefs["X2"] == pytest.approx(-2.0, abs=0.5)

def test_compute_lagged_correlations():
    np.random.seed(42)
    # y at time t correlates with x at time t - 1
    dates = pd.date_range("2024-01-01", periods=16, freq="MS").strftime("%Y-%m-%d")
    x = np.random.normal(100, 10, 16)
    y = np.zeros(16)
    for i in range(1, 16):
        y[i] = 2.0 * x[i-1] + np.random.normal(0, 2)
    y[0] = 2.0 * 100

    df = pd.DataFrame({"date": dates, "kpi_lead": x, "outcome": y})
    res = compute_lagged_correlations(df, "outcome", "kpi_lead", max_lags=2)
    assert res["success"] is True
    # Optimal lag should be 1 period
    assert res["optimal_lag_periods"] == 1
    assert res["peak_correlation"] > 0.85
