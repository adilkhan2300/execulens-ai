"""
ExecuLens AI - Financial Analysis & Variance Decomposition
Decomposes corporate profit variances into Revenue, COGS, OpEx, Price/Volume effects,
and analyzes Actual-versus-Budget discrepancies across Business Units and Regions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

def decompose_profit_variance(
    financial_df: pd.DataFrame,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None
) -> Dict[str, Any]:
    """
    Decompose total operating profit variance between two periods:
    Profit Change = Revenue Variance - COGS Variance - OpEx Variance.
    Also approximates Volume and Price/Mix contributions.
    """
    if financial_df is None or financial_df.empty:
        return {}

    sorted_dates = sorted(financial_df["date"].unique())
    if len(sorted_dates) < 2:
        return {}

    p1 = start_period if start_period in sorted_dates else sorted_dates[-2]
    p2 = end_period if end_period in sorted_dates else sorted_dates[-1]

    df_p1 = financial_df[financial_df["date"] == p1]
    df_p2 = financial_df[financial_df["date"] == p2]

    # Metrics Period 1
    rev_1 = float(df_p1["revenue"].sum())
    cogs_1 = float(df_p1["cost_of_goods_sold"].sum())
    opex_1 = float(df_p1["operating_expenses"].sum())
    op_1 = float(df_p1["operating_profit"].sum())
    orders_1 = float(df_p1["orders_count"].sum()) if "orders_count" in df_p1 else 1.0

    # Metrics Period 2
    rev_2 = float(df_p2["revenue"].sum())
    cogs_2 = float(df_p2["cost_of_goods_sold"].sum())
    opex_2 = float(df_p2["operating_expenses"].sum())
    op_2 = float(df_p2["operating_profit"].sum())
    orders_2 = float(df_p2["orders_count"].sum()) if "orders_count" in df_p2 else 1.0

    # Total Profit Change
    total_profit_change = op_2 - op_1
    rev_change = rev_2 - rev_1
    cogs_change = cogs_2 - cogs_1
    opex_change = opex_2 - opex_1

    # Price vs Volume breakdown
    # Volume effect = (Orders_2 - Orders_1) * (Rev_1 / Orders_1)
    aov_1 = rev_1 / orders_1 if orders_1 > 0 else 0
    aov_2 = rev_2 / orders_2 if orders_2 > 0 else 0
    volume_effect = (orders_2 - orders_1) * aov_1
    price_mix_effect = rev_change - volume_effect

    # Business Unit contribution to Profit Variance
    bu_p1 = df_p1.groupby("business_unit")["operating_profit"].sum()
    bu_p2 = df_p2.groupby("business_unit")["operating_profit"].sum()
    bu_variance = (bu_p2 - bu_p1).to_dict()

    # Region contribution to Profit Variance
    reg_p1 = df_p1.groupby("region")["operating_profit"].sum()
    reg_p2 = df_p2.groupby("region")["operating_profit"].sum()
    reg_variance = (reg_p2 - reg_p1).to_dict()

    # Waterfall Elements for Plotly
    # Starting Profit -> Volume Effect -> Price/Mix Effect -> -COGS Increase -> -OpEx Increase -> Ending Profit
    waterfall_items = [
        {"measure": "absolute", "name": f"Base Profit ({p1})", "value": op_1},
        {"measure": "relative", "name": "Volume Effect", "value": volume_effect},
        {"measure": "relative", "name": "Price/Mix Effect", "value": price_mix_effect},
        {"measure": "relative", "name": "COGS Impact", "value": -cogs_change},
        {"measure": "relative", "name": "OpEx Impact", "value": -opex_change},
        {"measure": "total", "name": f"Final Profit ({p2})", "value": op_2},
    ]

    return {
        "start_period": p1,
        "end_period": p2,
        "base_profit": op_1,
        "final_profit": op_2,
        "total_profit_change": total_profit_change,
        "pct_profit_change": (total_profit_change / abs(op_1) * 100.0) if op_1 != 0 else 0.0,
        "revenue_variance": rev_change,
        "cogs_variance": cogs_change,
        "opex_variance": opex_change,
        "volume_effect": volume_effect,
        "price_mix_effect": price_mix_effect,
        "bu_contributions": bu_variance,
        "region_contributions": reg_variance,
        "waterfall_items": waterfall_items,
    }


def analyze_budget_variances(
    financial_df: pd.DataFrame,
    period: Optional[str] = None
) -> pd.DataFrame:
    """
    Compare Actual vs Budget performance across Business Units and Regions.
    """
    if financial_df is None or financial_df.empty:
        return pd.DataFrame()

    df = financial_df.copy()
    if period:
        df = df[df["date"] == period]
    else:
        latest = df["date"].max()
        df = df[df["date"] == latest]

    agg = df.groupby(["business_unit", "region"]).agg(
        actual_revenue=("revenue", "sum"),
        budget_revenue=("budget_revenue", "sum"),
        actual_profit=("operating_profit", "sum"),
        budget_profit=("budget_operating_profit", "sum")
    ).reset_index()

    agg["rev_variance"] = agg["actual_revenue"] - agg["budget_revenue"]
    agg["rev_variance_pct"] = (agg["rev_variance"] / agg["budget_revenue"]) * 100.0
    agg["profit_variance"] = agg["actual_profit"] - agg["budget_profit"]
    agg["profit_variance_pct"] = (agg["profit_variance"] / agg["budget_profit"].abs()) * 100.0

    return agg
