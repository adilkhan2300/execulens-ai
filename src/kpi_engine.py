"""
ExecuLens AI - KPI Analytics Engine
Computes top-level executive KPI scorecards, period comparisons (MoM/QoQ),
target deviations, directional health scoring, and composite performance indexes.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from config.settings import KPI_DIRECTIONS

def evaluate_kpi_status(
    value: float,
    target: float,
    direction: str,
    warning_threshold: Optional[float] = None,
    critical_threshold: Optional[float] = None
) -> Tuple[str, str, float]:
    """
    Evaluate KPI status given direction and thresholds.
    Returns: (status: 'Healthy'|'Warning'|'Critical', sentiment: 'Favorable'|'Unfavorable'|'Neutral', pct_deviation)
    """
    if pd.isna(value) or pd.isna(target) or target == 0:
        return "Normal", "Neutral", 0.0

    pct_diff = ((value - target) / abs(target)) * 100.0

    if direction == "higher_is_better":
        if critical_threshold is not None and value <= critical_threshold:
            return "Critical", "Unfavorable", pct_diff
        elif warning_threshold is not None and value <= warning_threshold:
            return "Warning", "Unfavorable", pct_diff
        elif value >= target:
            return "Healthy", "Favorable", pct_diff
        else:
            return "Warning", "Unfavorable", pct_diff

    elif direction == "lower_is_better":
        if critical_threshold is not None and value >= critical_threshold:
            return "Critical", "Unfavorable", pct_diff
        elif warning_threshold is not None and value >= warning_threshold:
            return "Warning", "Unfavorable", pct_diff
        elif value <= target:
            return "Healthy", "Favorable", pct_diff
        else:
            return "Warning", "Unfavorable", pct_diff

    elif direction == "target_range":
        # Target range: warning if outside +/- 15%, critical if outside +/- 25%
        abs_dev = abs(pct_diff)
        if abs_dev > 25.0:
            return "Critical", "Unfavorable", pct_diff
        elif abs_dev > 15.0:
            return "Warning", "Unfavorable", pct_diff
        else:
            return "Healthy", "Favorable", pct_diff

    return "Healthy", "Neutral", pct_diff


def compute_executive_scorecard(financial_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute top-level executive scorecard cards:
    Revenue, Operating Profit, Operating Margin, Cash Flow, Budget Achievement,
    MoM Revenue Growth, MoM Profit Growth, and Overall Performance Score.
    """
    if financial_df is None or financial_df.empty:
        return {}

    # Sort chronologically
    df_sorted = financial_df.sort_values("date")
    unique_dates = df_sorted["date"].unique()
    
    if len(unique_dates) == 0:
        return {}

    # Current period (latest date)
    curr_date = unique_dates[-1]
    df_curr = df_sorted[df_sorted["date"] == curr_date]
    
    # Previous period
    has_prev = len(unique_dates) > 1
    prev_date = unique_dates[-2] if has_prev else curr_date
    df_prev = df_sorted[df_sorted["date"] == prev_date]

    # Current Totals
    curr_rev = float(df_curr["revenue"].sum())
    curr_cogs = float(df_curr["cost_of_goods_sold"].sum())
    curr_opex = float(df_curr["operating_expenses"].sum())
    curr_gp = float(df_curr["gross_profit"].sum())
    curr_op = float(df_curr["operating_profit"].sum())
    curr_cf = float(df_curr["cash_flow"].sum()) if "cash_flow" in df_curr else 0.0
    curr_budget_rev = float(df_curr["budget_revenue"].sum()) if "budget_revenue" in df_curr else curr_rev
    curr_budget_op = float(df_curr["budget_operating_profit"].sum()) if "budget_operating_profit" in df_curr else curr_op
    
    curr_margin = (curr_op / curr_rev * 100.0) if curr_rev > 0 else 0.0

    # Previous Totals
    prev_rev = float(df_prev["revenue"].sum())
    prev_op = float(df_prev["operating_profit"].sum())
    prev_margin = (prev_op / prev_rev * 100.0) if prev_rev > 0 else 0.0
    prev_cf = float(df_prev["cash_flow"].sum()) if "cash_flow" in df_prev else 0.0

    # Growth & Variances
    rev_growth = ((curr_rev - prev_rev) / prev_rev * 100.0) if prev_rev > 0 else 0.0
    profit_growth = ((curr_op - prev_op) / abs(prev_op) * 100.0) if prev_op != 0 else 0.0
    margin_change = curr_margin - prev_margin
    budget_achievement = (curr_rev / curr_budget_rev * 100.0) if curr_budget_rev > 0 else 100.0
    profit_budget_achievement = (curr_op / curr_budget_op * 100.0) if curr_budget_op != 0 else 100.0

    # Composite Business Performance Index (0-100)
    # Weights: Revenue Growth (25%), Profit Margin (25%), Budget Achievement (30%), Cash Flow Ratio (20%)
    norm_rev_growth = np.clip(50 + rev_growth * 5, 0, 100)
    norm_margin = np.clip(curr_margin * 4, 0, 100)
    norm_budget = np.clip(budget_achievement, 0, 100)
    cf_to_op = (curr_cf / curr_op) if curr_op > 0 else 0.8
    norm_cf = np.clip(cf_to_op * 80, 0, 100)

    perf_score = (
        0.25 * norm_rev_growth +
        0.25 * norm_margin +
        0.30 * norm_budget +
        0.20 * norm_cf
    )

    return {
        "current_period": curr_date,
        "previous_period": prev_date,
        "revenue": {
            "value": curr_rev,
            "prev_value": prev_rev,
            "change_pct": rev_growth,
            "favorable": rev_growth >= 0,
            "target": curr_budget_rev,
            "target_achievement": budget_achievement,
        },
        "operating_profit": {
            "value": curr_op,
            "prev_value": prev_op,
            "change_pct": profit_growth,
            "favorable": profit_growth >= 0,
            "target": curr_budget_op,
            "target_achievement": profit_budget_achievement,
        },
        "operating_margin": {
            "value": curr_margin,
            "prev_value": prev_margin,
            "change_pts": margin_change,
            "favorable": margin_change >= 0,
        },
        "cash_flow": {
            "value": curr_cf,
            "prev_value": prev_cf,
            "change_pct": ((curr_cf - prev_cf) / abs(prev_cf) * 100.0) if prev_cf != 0 else 0.0,
            "favorable": curr_cf >= prev_cf,
        },
        "gross_profit": {
            "value": curr_gp,
            "margin_pct": (curr_gp / curr_rev * 100.0) if curr_rev > 0 else 0.0,
        },
        "cogs": {
            "value": curr_cogs,
            "pct_of_rev": (curr_cogs / curr_rev * 100.0) if curr_rev > 0 else 0.0,
        },
        "opex": {
            "value": curr_opex,
            "pct_of_rev": (curr_opex / curr_rev * 100.0) if curr_rev > 0 else 0.0,
        },
        "budget_achievement": budget_achievement,
        "performance_score": round(float(perf_score), 1),
    }


def aggregate_kpi_summary(
    operational_df: pd.DataFrame,
    kpi_defs_dict: Dict[str, Dict[str, Any]],
    current_date: Optional[str] = None
) -> pd.DataFrame:
    """
    Generate an executive KPI summary table with current values, targets,
    variances, and health status (Healthy, Warning, Critical).
    """
    if operational_df is None or operational_df.empty:
        return pd.DataFrame()

    df = operational_df.copy()
    if current_date:
        df = df[df["date"] == current_date]
    else:
        latest_date = df["date"].max()
        df = df[df["date"] == latest_date]

    # Aggregate across units and regions
    grouped = df.groupby(["department", "kpi_name", "kpi_unit"]).agg(
        current_value=("kpi_value", "mean"),
        target_value=("target_value", "first"),
        prev_value=("previous_period_value", "mean")
    ).reset_index()

    records = []
    for _, row in grouped.iterrows():
        kpi_name = row["kpi_name"]
        meta = kpi_defs_dict.get(kpi_name, {})
        direction = meta.get("direction", "higher_is_better")
        warn_th = meta.get("warning_threshold")
        crit_th = meta.get("critical_threshold")
        desc = meta.get("description", "")
        owner = meta.get("business_owner", "Unassigned")
        linked_outcome = meta.get("linked_financial_outcome", "revenue")

        curr_v = float(row["current_value"])
        target_v = float(row["target_value"]) if pd.notna(row["target_value"]) else curr_v
        prev_v = float(row["prev_value"]) if pd.notna(row["prev_value"]) else curr_v

        status, sentiment, pct_dev = evaluate_kpi_status(
            curr_v, target_v, direction, warn_th, crit_th
        )

        mom_change = ((curr_v - prev_v) / abs(prev_v) * 100.0) if prev_v != 0 else 0.0

        records.append({
            "department": row["department"],
            "kpi_name": kpi_name,
            "kpi_unit": row["kpi_unit"],
            "current_value": round(curr_v, 2),
            "target_value": round(target_v, 2),
            "previous_value": round(prev_v, 2),
            "mom_change_pct": round(mom_change, 2),
            "target_deviation_pct": round(pct_dev, 2),
            "direction": direction,
            "status": status,
            "sentiment": sentiment,
            "business_owner": owner,
            "linked_outcome": linked_outcome,
            "description": desc,
        })

    return pd.DataFrame(records)
