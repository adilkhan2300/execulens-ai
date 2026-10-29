"""
ExecuLens AI - Lagged Relationship Analysis Engine
Investigates delayed operational effects on financial outcomes over configurable
lag horizons (e.g., 0 to 3 months / 0 to 90 days), detects peak lag correlation,
and assesses statistical viability without overstating delayed causal effects.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Any, Optional

def compute_lagged_correlations(
    merged_monthly_df: pd.DataFrame,
    target_outcome: str,
    kpi_name: str,
    max_lags: int = 3
) -> Dict[str, Any]:
    """
    Compute correlation between an operational KPI at time (t - lag) and
    a financial outcome at time (t).
    max_lags: number of historical monthly periods to shift (e.g. 0, 1, 2, 3 months).
    """
    if merged_monthly_df.empty or target_outcome not in merged_monthly_df.columns or kpi_name not in merged_monthly_df.columns:
        return {"success": False, "error": "Columns missing from input matrix"}

    # Must be strictly sorted chronologically
    df_sorted = merged_monthly_df.sort_values("date").copy()
    
    # Check observations
    n_obs = len(df_sorted)
    if n_obs < max_lags + 6:
        return {
            "success": False,
            "error": f"Sample size ({n_obs}) too small for reliable lag analysis up to {max_lags} periods. Minimum {max_lags + 6} required."
        }

    lag_results = []
    y = df_sorted[target_outcome].values

    for lag in range(0, max_lags + 1):
        if lag == 0:
            x_lagged = df_sorted[kpi_name].values
            y_curr = y
        else:
            # Shift KPI backward so that KPI[t - lag] aligns with Outcome[t]
            x_lagged = df_sorted[kpi_name].shift(lag).values[lag:]
            y_curr = y[lag:]

        valid_mask = (~np.isnan(x_lagged)) & (~np.isnan(y_curr))
        valid_n = int(np.sum(valid_mask))

        if valid_n >= 5 and np.std(x_lagged[valid_mask]) > 0 and np.std(y_curr[valid_mask]) > 0:
            r, p = stats.pearsonr(x_lagged[valid_mask], y_curr[valid_mask])
            rho, rho_p = stats.spearmanr(x_lagged[valid_mask], y_curr[valid_mask])
            
            lag_days = lag * 30  # Approx 30 days per monthly period
            
            lag_results.append({
                "lag_periods": lag,
                "lag_approx_days": lag_days,
                "pearson_r": round(float(r), 3),
                "pearson_p_value": round(float(p), 4),
                "spearman_rho": round(float(rho), 3),
                "sample_size": valid_n,
                "is_significant": p < 0.05
            })

    if not lag_results:
        return {"success": False, "error": "Insufficient valid points for lag computation"}

    # Find optimal lag (highest absolute correlation)
    optimal_entry = max(lag_results, key=lambda x: abs(x["pearson_r"]))

    return {
        "success": True,
        "kpi_name": kpi_name,
        "target_outcome": target_outcome,
        "optimal_lag_periods": optimal_entry["lag_periods"],
        "optimal_lag_days": optimal_entry["lag_approx_days"],
        "peak_correlation": optimal_entry["pearson_r"],
        "peak_p_value": optimal_entry["pearson_p_value"],
        "lag_series": lag_results,
        "sample_size_base": n_obs,
    }


def batch_lag_screening(
    merged_monthly_df: pd.DataFrame,
    target_outcome: str,
    kpi_columns: List[str],
    max_lags: int = 3
) -> pd.DataFrame:
    """
    Screen all operational KPIs across lag horizons to discover delayed drivers.
    """
    rows = []
    for kpi in kpi_columns:
        res = compute_lagged_correlations(merged_monthly_df, target_outcome, kpi, max_lags=max_lags)
        if res.get("success"):
            rows.append({
                "kpi_name": kpi,
                "target_outcome": target_outcome,
                "optimal_lag_months": res["optimal_lag_periods"],
                "optimal_lag_days": res["optimal_lag_days"],
                "peak_r": res["peak_correlation"],
                "p_value": res["peak_p_value"],
                "direction": "Positive" if res["peak_correlation"] > 0 else "Negative",
                "is_delayed_driver": res["optimal_lag_periods"] > 0 and abs(res["peak_correlation"]) >= 0.4
            })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(by="peak_r", key=abs, ascending=False).reset_index(drop=True)
    return df
