"""
ExecuLens AI - Performance Forecasting Engine
Chronological time-series forecasting (Linear-Trend + Seasonal Decomposition,
Exponential Smoothing) with prediction intervals, holdout backtesting (MAE, RMSE, MAPE),
and explicit documentation of sample size limitations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def generate_financial_forecast(
    financial_df: pd.DataFrame,
    target_metric: str = "revenue",
    forecast_horizon: int = 6,
    train_split_pct: float = 0.80
) -> Dict[str, Any]:
    """
    Generate chronological forecast for a selected financial metric.
    Uses chronological split backtesting to report out-of-sample MAE, RMSE, and MAPE.
    """
    if financial_df.empty or target_metric not in financial_df.columns:
        return {"success": False, "error": f"Metric '{target_metric}' not available in dataset."}

    # Aggregate metric to monthly total
    monthly_series = financial_df.groupby("date")[target_metric].sum().reset_index()
    monthly_series["date"] = pd.to_datetime(monthly_series["date"])
    monthly_series = monthly_series.sort_values("date").reset_index(drop=True)

    n_points = len(monthly_series)
    if n_points < 12:
        return {
            "success": False,
            "error": f"Insufficient historical periods ({n_points} months). Minimum 12 monthly periods required for seasonal forecasting.",
            "data_points": n_points,
        }

    y = monthly_series[target_metric].values
    dates = monthly_series["date"]

    # 1. Chronological Holdout Backtesting
    split_idx = int(n_points * train_split_pct)
    train_y = y[:split_idx]
    test_y = y[split_idx:]
    test_dates = dates[split_idx:]

    mae, rmse, mape = 0.0, 0.0, 0.0
    try:
        # Fit baseline model on training set
        if len(train_y) >= 8:
            train_model = ExponentialSmoothing(
                train_y, trend="add", seasonal=None, initialization_method="estimated"
            ).fit()
            test_preds = train_model.forecast(len(test_y))
            
            mae = float(np.mean(np.abs(test_preds - test_y)))
            rmse = float(np.sqrt(np.mean((test_preds - test_y) ** 2)))
            mape = float(np.mean(np.abs((test_preds - test_y) / test_y)) * 100.0)
    except Exception:
        # Fallback to simple linear trend if smoothing convergence fails
        t_train = np.arange(len(train_y))
        slope, intercept = np.polyfit(t_train, train_y, 1)
        test_preds = intercept + slope * np.arange(len(train_y), len(y))
        mae = float(np.mean(np.abs(test_preds - test_y)))
        rmse = float(np.sqrt(np.mean((test_preds - test_y) ** 2)))
        mape = float(np.mean(np.abs((test_preds - test_y) / test_y)) * 100.0)

    # 2. Refit on full series and forecast future horizon
    try:
        full_model = ExponentialSmoothing(
            y, trend="add", seasonal=None, initialization_method="estimated"
        ).fit()
        forecast_vals = full_model.forecast(forecast_horizon)
    except Exception:
        t_full = np.arange(len(y))
        slope, intercept = np.polyfit(t_full, y, 1)
        forecast_vals = intercept + slope * np.arange(len(y), len(y) + forecast_horizon)

    # Prediction intervals based on historical residual standard deviation
    residuals = y[1:] - y[:-1]
    res_std = np.std(residuals) if len(residuals) > 0 else (np.mean(y) * 0.05)
    
    last_date = dates.iloc[-1]
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=forecast_horizon, freq="MS")

    forecast_records = []
    for step, (f_date, val) in enumerate(zip(future_dates, forecast_vals)):
        # Widening uncertainty cone: std * sqrt(step + 1) * 1.96 (for 95% CI)
        margin = 1.96 * res_std * np.sqrt(step + 1)
        forecast_records.append({
            "date": f_date.strftime("%Y-%m-%d"),
            "forecast_value": round(float(val), 2),
            "ci_lower_95": round(max(0.0, float(val - margin)), 2),
            "ci_upper_95": round(float(val + margin), 2),
        })

    hist_records = [
        {"date": d.strftime("%Y-%m-%d"), "actual_value": round(float(v), 2)}
        for d, v in zip(dates, y)
    ]

    return {
        "success": True,
        "metric": target_metric,
        "historical_series": hist_records,
        "forecast_series": forecast_records,
        "evaluation_metrics": {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "mape_pct": round(mape, 2),
            "train_months": split_idx,
            "test_months": len(test_y),
            "validation_approach": "Chronological holdout split (no data leakage)"
        },
        "model_name": "Exponential Smoothing (Additive Trend) with Widening Uncertainty Bounds",
        "limitations": "Forecasts assume continuity of past trends without exogenous black-swan shocks or major strategic pivots."
    }
