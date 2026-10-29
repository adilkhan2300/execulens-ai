"""
ExecuLens AI - Scenario Simulator & Sensitivity Analysis Engine
Enables executive what-if simulation, sensitivity grids, and multi-scenario comparisons
with clear formulas, avoidance of double counting, and transparent assumptions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

def get_baseline_operating_state(financial_df: pd.DataFrame, period: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract aggregated financial and operational baseline from the selected or latest period.
    """
    if financial_df.empty:
        return {}

    p = period or financial_df["date"].max()
    df_p = financial_df[financial_df["date"] == p]

    rev = float(df_p["revenue"].sum())
    cogs = float(df_p["cost_of_goods_sold"].sum())
    opex = float(df_p["operating_expenses"].sum())
    op = float(df_p["operating_profit"].sum())
    orders = int(df_p["orders_count"].sum()) if "orders_count" in df_p else 1000
    customers = int(df_p["customer_count"].sum()) if "customer_count" in df_p else int(orders * 0.7)

    aov = rev / orders if orders > 0 else 3500.0
    cogs_rate = cogs / rev if rev > 0 else 0.48
    fulfillment_cost_est = (cogs * 0.22) / orders if orders > 0 else 18.0

    return {
        "period": p,
        "revenue": rev,
        "cogs": cogs,
        "operating_expenses": opex,
        "operating_profit": op,
        "operating_margin_pct": (op / rev * 100.0) if rev > 0 else 0.0,
        "orders_count": orders,
        "customer_count": customers,
        "average_order_value": aov,
        "cogs_ratio": cogs_rate,
        "fulfillment_cost_per_order": fulfillment_cost_est,
    }


def simulate_what_if_scenario(
    baseline: Dict[str, Any],
    conversion_rate_delta_pct: float = 0.0,
    aov_delta_pct: float = 0.0,
    cac_delta_pct: float = 0.0,
    fulfillment_cost_delta_pct: float = 0.0,
    turnover_reduction_pct: float = 0.0,
    stockout_reduction_pct: float = 0.0,
    scenario_name: str = "Custom What-If"
) -> Dict[str, Any]:
    """
    Simulate financial results given percentage modifications to key operational drivers.
    All delta percentages are entered as values like +5.0 for +5% increase or -10.0 for -10% decrease.
    """
    base_rev = baseline.get("revenue", 1_000_000.0)
    base_orders = baseline.get("orders_count", 1000)
    base_aov = baseline.get("average_order_value", 3500.0)
    base_cogs = baseline.get("cogs", 480_000.0)
    base_opex = baseline.get("operating_expenses", 330_000.0)
    base_profit = baseline.get("operating_profit", 190_000.0)
    base_customers = baseline.get("customer_count", 700)

    # 1. Volume & Revenue effects
    # Conversion rate change alters order volume directly
    new_orders = base_orders * (1.0 + conversion_rate_delta_pct / 100.0)
    # Stockout reduction recaptures lost sales (+0.25% orders per 10% stockout reduction)
    stockout_recapture_orders = base_orders * (stockout_reduction_pct / 100.0 * 0.025)
    total_sim_orders = new_orders + stockout_recapture_orders

    new_aov = base_aov * (1.0 + aov_delta_pct / 100.0)
    sim_revenue = total_sim_orders * new_aov

    # 2. Cost of Goods Sold effects
    # Base COGS variable portion scales with orders; fulfillment cost changes directly adjust COGS
    base_cogs_ratio = base_cogs / base_rev if base_rev > 0 else 0.48
    sim_cogs = sim_revenue * base_cogs_ratio
    # Fulfillment cost adjustment
    fulfillment_impact = base_orders * (baseline.get("fulfillment_cost_per_order", 18.0) * (fulfillment_cost_delta_pct / 100.0))
    sim_cogs += fulfillment_impact

    # 3. Operating Expenses effects
    sim_opex = base_opex
    # CAC impact: approx 25% of OpEx is acquisition spend
    mktg_acquisition_spend = base_opex * 0.25
    sim_opex += mktg_acquisition_spend * (cac_delta_pct / 100.0)
    # Turnover reduction saves recruitment & onboarding (approx $15K per 10% turnover reduction)
    turnover_savings = (turnover_reduction_pct / 100.0) * 25_000.0
    sim_opex -= turnover_savings

    # 4. Simulated Operating Profit
    sim_profit = sim_revenue - sim_cogs - sim_opex
    sim_margin = (sim_profit / sim_revenue * 100.0) if sim_revenue > 0 else 0.0

    # Variances
    rev_delta = sim_revenue - base_rev
    profit_delta = sim_profit - base_profit
    margin_delta = sim_margin - baseline.get("operating_margin_pct", 0.0)

    return {
        "scenario_name": scenario_name,
        "simulated_revenue": round(sim_revenue, 2),
        "simulated_cogs": round(sim_cogs, 2),
        "simulated_opex": round(sim_opex, 2),
        "simulated_operating_profit": round(sim_profit, 2),
        "simulated_margin_pct": round(sim_margin, 2),
        "simulated_orders": int(total_sim_orders),
        "revenue_delta": round(rev_delta, 2),
        "revenue_delta_pct": round((rev_delta / base_rev * 100.0) if base_rev > 0 else 0.0, 2),
        "profit_delta": round(profit_delta, 2),
        "profit_delta_pct": round((profit_delta / abs(base_profit) * 100.0) if base_profit != 0 else 0.0, 2),
        "margin_delta_pts": round(margin_delta, 2),
        "assumptions": {
            "conversion_delta_pct": conversion_rate_delta_pct,
            "aov_delta_pct": aov_delta_pct,
            "cac_delta_pct": cac_delta_pct,
            "fulfillment_cost_delta_pct": fulfillment_cost_delta_pct,
            "turnover_reduction_pct": turnover_reduction_pct,
            "stockout_reduction_pct": stockout_reduction_pct,
        }
    }


def generate_scenario_matrix_comparison(baseline: Dict[str, Any]) -> pd.DataFrame:
    """
    Generate standard 5-way executive scenario comparison:
    1. Business as Usual (BAU)
    2. Cost Optimization
    3. Growth Acceleration
    4. Operational Excellence
    5. Integrated Strategic Plan
    """
    scenarios = [
        simulate_what_if_scenario(baseline, 0, 0, 0, 0, 0, 0, scenario_name="1. Business As Usual (BAU)"),
        simulate_what_if_scenario(baseline, 0, 0, -10, -8, 15, 0, scenario_name="2. Cost Reduction Program"),
        simulate_what_if_scenario(baseline, 8, 4, 10, 0, 0, 20, scenario_name="3. Revenue Acceleration"),
        simulate_what_if_scenario(baseline, 4, 0, -5, -12, 20, 35, scenario_name="4. Operational Excellence"),
        simulate_what_if_scenario(baseline, 10, 5, -8, -10, 25, 40, scenario_name="5. Combined Strategic Transformation"),
    ]

    rows = []
    for s in scenarios:
        rows.append({
            "Scenario Name": s["scenario_name"],
            "Revenue": s["simulated_revenue"],
            "Revenue Delta": s["revenue_delta"],
            "Operating Profit": s["simulated_operating_profit"],
            "Profit Delta": s["profit_delta"],
            "Profit Growth (%)": s["profit_delta_pct"],
            "Operating Margin (%)": s["simulated_margin_pct"],
        })

    return pd.DataFrame(rows)


def compute_2d_sensitivity_grid(
    baseline: Dict[str, Any],
    row_lever_name: str = "conversion_rate_delta_pct",
    col_lever_name: str = "cac_delta_pct",
    row_steps: List[float] = [-10, -5, 0, 5, 10],
    col_steps: List[float] = [-15, -7.5, 0, 7.5, 15]
) -> pd.DataFrame:
    """
    Compute a 2D sensitivity grid for Operating Profit outcomes.
    """
    grid = {}
    for r_val in row_steps:
        row_dict = {}
        for c_val in col_steps:
            kwargs = {row_lever_name: r_val, col_lever_name: c_val}
            res = simulate_what_if_scenario(baseline, **kwargs)
            row_dict[f"{col_lever_name.split('_')[0].upper()} {c_val:+.1f}%"] = res["simulated_operating_profit"]
        grid[f"{row_lever_name.split('_')[0].upper()} {r_val:+.1f}%"] = row_dict

    return pd.DataFrame(grid).T
