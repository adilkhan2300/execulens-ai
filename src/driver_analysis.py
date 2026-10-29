"""
ExecuLens AI - KPI Driver Analysis Engine
Identifies operational indicators associated with key financial outcomes
using Pearson, Spearman, Multivariable OLS regression, Random Forest importance,
and computes an explainable multi-factor Driver Prioritization Score.
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
import statsmodels.api as sm
from typing import Dict, List, Any, Optional, Tuple
from config.settings import DRIVER_SCORE_WEIGHTS

def build_aligned_analysis_matrix(
    financial_df: pd.DataFrame,
    operational_df: pd.DataFrame,
    grain: str = "monthly_bu_region" # "monthly_bu_region" or "monthly_aggregate"
) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """
    Pivot operational KPIs into wide format and align with financial outcomes.
    Returns: (merged_df, kpi_columns, outcome_columns)
    """
    if financial_df.empty or operational_df.empty:
        return pd.DataFrame(), [], []

    # Financial outcomes
    fin_df = financial_df.copy()
    if "operating_margin" not in fin_df.columns:
        fin_df["operating_margin"] = (fin_df["operating_profit"] / fin_df["revenue"] * 100.0).fillna(0)
    if "revenue_per_employee" not in fin_df.columns:
        # Approximate headcount proxy if not directly recorded
        fin_df["revenue_per_employee"] = fin_df["revenue"] / np.clip(fin_df["customer_count"] * 0.15, 10, 500)

    if grain == "monthly_bu_region":
        join_keys = ["date", "business_unit", "region"]
        
        # Aggregate financial to grain
        fin_agg = fin_df.groupby(join_keys).agg(
            revenue=("revenue", "sum"),
            operating_profit=("operating_profit", "sum"),
            operating_margin=("operating_margin", "mean"),
            cash_flow=("cash_flow", "sum"),
            customer_count=("customer_count", "sum"),
            revenue_per_employee=("revenue_per_employee", "mean")
        ).reset_index()

        # Operational KPIs wide format
        ops_pivot = operational_df.pivot_table(
            index=join_keys,
            columns="kpi_name",
            values="kpi_value",
            aggfunc="mean"
        ).reset_index()

        merged = pd.merge(fin_agg, ops_pivot, on=join_keys, how="inner")

    else:
        # Monthly aggregate
        join_keys = ["date"]
        fin_agg = fin_df.groupby("date").agg(
            revenue=("revenue", "sum"),
            operating_profit=("operating_profit", "sum"),
            operating_margin=("operating_margin", "mean"),
            cash_flow=("cash_flow", "sum"),
            customer_count=("customer_count", "sum"),
            revenue_per_employee=("revenue_per_employee", "mean")
        ).reset_index()

        ops_pivot = operational_df.pivot_table(
            index="date",
            columns="kpi_name",
            values="kpi_value",
            aggfunc="mean"
        ).reset_index()

        merged = pd.merge(fin_agg, ops_pivot, on="date", how="inner")

    outcome_cols = ["revenue", "operating_profit", "operating_margin", "cash_flow", "customer_count", "revenue_per_employee"]
    kpi_cols = [c for c in ops_pivot.columns if c not in join_keys]

    return merged, kpi_cols, outcome_cols


def analyze_kpi_correlations(
    merged_df: pd.DataFrame,
    target_outcome: str,
    kpi_columns: List[str],
    kpi_defs_dict: Optional[Dict[str, Dict[str, Any]]] = None
) -> pd.DataFrame:
    """
    Compute Pearson & Spearman correlation, p-values, sample size,
    stability across chronological halves, and explainable Driver Score.
    """
    if merged_df.empty or target_outcome not in merged_df.columns:
        return pd.DataFrame()

    results = []
    defs = kpi_defs_dict or {}
    y = merged_df[target_outcome].values

    # Chronological half split for stability testing
    n_rows = len(merged_df)
    half_n = n_rows // 2
    y_h1 = y[:half_n]
    y_h2 = y[half_n:]

    for kpi in kpi_columns:
        if kpi not in merged_df.columns:
            continue

        x = merged_df[kpi].values
        valid_mask = (~np.isnan(x)) & (~np.isnan(y))
        valid_n = int(np.sum(valid_mask))

        if valid_n < 6 or np.std(x[valid_mask]) == 0 or np.std(y[valid_mask]) == 0:
            # Insufficient variance or sample size
            continue

        x_clean = x[valid_mask]
        y_clean = y[valid_mask]

        # 1. Pearson
        pearson_r, pearson_p = stats.pearsonr(x_clean, y_clean)
        # 2. Spearman
        spearman_r, spearman_p = stats.spearmanr(x_clean, y_clean)

        # 3. Stability check (difference in Pearson r between period halves)
        mask_h1 = (~np.isnan(x[:half_n])) & (~np.isnan(y_h1))
        mask_h2 = (~np.isnan(x[half_n:])) & (~np.isnan(y_h2))
        if np.sum(mask_h1) > 4 and np.sum(mask_h2) > 4:
            r1, _ = stats.pearsonr(x[:half_n][mask_h1], y_h1[mask_h1])
            r2, _ = stats.pearsonr(x[half_n:][mask_h2], y_h2[mask_h2])
            r_diff = abs(r1 - r2)
            stability_score = max(0.0, 1.0 - (r_diff / 2.0))
        else:
            stability_score = 0.5

        # Metadata context
        meta = defs.get(kpi, {})
        dept = meta.get("department", "Operations")
        target_val = meta.get("target_value", np.mean(x_clean))
        expected_outcome = meta.get("linked_financial_outcome", "")
        direction = meta.get("direction", "higher_is_better")

        # Target deviation
        if target_val != 0:
            avg_val = np.mean(x_clean)
            target_dev = min(1.0, abs((avg_val - target_val) / target_val))
        else:
            target_dev = 0.0

        # Financial relevance boost if explicitly linked in metadata
        fin_relevance = 1.0 if expected_outcome.lower() == target_outcome.lower() else 0.65

        # Statistical reliability = 1 - p_value
        stat_reliability = max(0.0, 1.0 - pearson_p)

        # Composite Explainable Driver Score (0-100)
        # Formula: w1*|r| + w2*(1-p) + w3*stability + w4*dev + w5*relevance
        w = DRIVER_SCORE_WEIGHTS
        raw_score = (
            w["association_strength"] * abs(pearson_r) +
            w["statistical_reliability"] * stat_reliability +
            w["stability"] * stability_score +
            w["target_deviation"] * target_dev +
            w["financial_relevance"] * fin_relevance
        ) * 100.0

        direction_label = "Positive" if pearson_r > 0 else "Negative"

        # Statistical significance level
        if pearson_p < 0.01:
            sig_label = "High (p < 0.01)"
        elif pearson_p < 0.05:
            sig_label = "Moderate (p < 0.05)"
        else:
            sig_label = "Low (p >= 0.05)"

        results.append({
            "kpi_name": kpi,
            "department": dept,
            "target_outcome": target_outcome,
            "direction_of_association": direction_label,
            "pearson_r": round(float(pearson_r), 3),
            "pearson_p_value": round(float(pearson_p), 4),
            "spearman_r": round(float(spearman_r), 3),
            "spearman_p_value": round(float(spearman_p), 4),
            "significance": sig_label,
            "sample_size": valid_n,
            "stability_score": round(float(stability_score * 100), 1),
            "driver_score": round(float(raw_score), 1),
            "expected_outcome_link": expected_outcome,
        })

    df_res = pd.DataFrame(results)
    if not df_res.empty:
        df_res = df_res.sort_values("driver_score", ascending=False).reset_index(drop=True)
    return df_res


def run_multivariable_regression(
    merged_df: pd.DataFrame,
    target_outcome: str,
    top_kpis: List[str]
) -> Dict[str, Any]:
    """
    Fit an Ordinary Least Squares (OLS) multivariable regression model
    for the selected top operational indicators against the financial outcome.
    Provides coefficients, standard errors, p-values, 95% CIs, and R-squared.
    """
    if merged_df.empty or not top_kpis or target_outcome not in merged_df.columns:
        return {"success": False, "error": "Insufficient data"}

    valid_cols = [c for c in top_kpis if c in merged_df.columns]
    if len(valid_cols) == 0:
        return {"success": False, "error": "No valid KPI columns"}

    sub_df = merged_df[[target_outcome] + valid_cols].dropna()
    if len(sub_df) < len(valid_cols) + 5:
        return {
            "success": False,
            "error": f"Sample size ({len(sub_df)}) too small for {len(valid_cols)} features"
        }

    X = sub_df[valid_cols]
    y = sub_df[target_outcome]

    # Add constant intercept
    X_with_const = sm.add_constant(X)

    try:
        model = sm.OLS(y, X_with_const).fit()
        
        coef_table = []
        conf_int = model.conf_int()
        
        for col in valid_cols:
            coef = model.params.get(col, 0.0)
            p_val = model.pvalues.get(col, 1.0)
            stderr = model.bse.get(col, 0.0)
            ci_low = conf_int.loc[col, 0] if col in conf_int.index else 0.0
            ci_high = conf_int.loc[col, 1] if col in conf_int.index else 0.0
            
            coef_table.append({
                "feature": col,
                "coefficient": round(float(coef), 4),
                "std_error": round(float(stderr), 4),
                "p_value": round(float(p_val), 4),
                "conf_interval_95": f"[{ci_low:.2f}, {ci_high:.2f}]",
                "statistically_significant": p_val < 0.05,
            })

        return {
            "success": True,
            "target_outcome": target_outcome,
            "r_squared": round(float(model.rsquared), 3),
            "adj_r_squared": round(float(model.rsquared_adj), 3),
            "f_statistic": round(float(model.fvalue), 2) if model.fvalue is not None else 0.0,
            "f_pvalue": round(float(model.f_pvalue), 4) if model.f_pvalue is not None else 1.0,
            "sample_size": len(sub_df),
            "coefficients": coef_table,
            "summary_text": str(model.summary()),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
