"""
ExecuLens AI - Financial Impact Modeling Engine
Translates operational KPI deviations into defensible, business-relevant financial estimates
with explicit mathematical formulas, low/base/high uncertainty scenarios, and documented assumptions.
"""

from typing import Dict, List, Any, Optional

def model_conversion_rate_impact(
    base_orders: int,
    avg_order_value: float,
    current_rate: float,
    target_rate: float,
    confidence_spread: float = 0.20
) -> Dict[str, Any]:
    """
    Model estimated revenue impact from sales conversion rate variance.
    Formula: Estimated Lost/Gained Orders = Base Orders * ((Current - Target) / Target)
             Revenue Impact = Lost/Gained Orders * Average Order Value
    """
    if target_rate <= 0:
        return {}

    pct_diff = (current_rate - target_rate) / target_rate
    delta_orders = base_orders * pct_diff
    base_impact = delta_orders * avg_order_value

    low_impact = base_impact * (1.0 - confidence_spread)
    high_impact = base_impact * (1.0 + confidence_spread)

    return {
        "kpi_name": "Sales Conversion Rate",
        "current_rate_pct": current_rate,
        "target_rate_pct": target_rate,
        "estimated_order_delta": round(delta_orders, 0),
        "impact_type": "Revenue Uplift" if base_impact >= 0 else "Revenue Loss / Opportunity Cost",
        "base_financial_impact": round(base_impact, 2),
        "low_scenario": round(min(low_impact, high_impact), 2),
        "high_scenario": round(max(low_impact, high_impact), 2),
        "formula": "Order Delta = Base Orders * ((Current Rate - Target Rate) / Target Rate); Impact = Order Delta * AOV",
        "assumptions": f"Assumes average order value of ${avg_order_value:,.2f} remains constant across order elasticity.",
        "uncertainty_rating": "+/- 20% scenario bounds",
    }


def model_cac_impact(
    new_customers_acquired: int,
    current_cac: float,
    target_cac: float,
    confidence_spread: float = 0.15
) -> Dict[str, Any]:
    """
    Model marketing budget variance caused by Customer Acquisition Cost deviations.
    Formula: Financial Variance = (Current CAC - Target CAC) * New Customers
    """
    delta_cac = current_cac - target_cac
    base_impact = delta_cac * new_customers_acquired  # Positive means higher cost (adverse)

    return {
        "kpi_name": "Customer Acquisition Cost",
        "current_cac": current_cac,
        "target_cac": target_cac,
        "new_customers": new_customers_acquired,
        "impact_type": "Increased Marketing Expense" if base_impact > 0 else "Marketing Efficiency Savings",
        "base_financial_impact": round(-base_impact, 2),  # Profit impact (negative if cost is higher)
        "low_scenario": round(-base_impact * (1.0 + confidence_spread), 2),
        "high_scenario": round(-base_impact * (1.0 - confidence_spread), 2),
        "formula": "Expense Impact = (Current CAC - Target CAC) * New Customers Acquired",
        "assumptions": "Calculated on acquired customer cohort; assumes linear acquisition cost elasticity.",
        "uncertainty_rating": "+/- 15% scenario bounds",
    }


def model_stockout_impact(
    total_orders_demand: int,
    avg_order_value: float,
    stockout_rate_pct: float,
    target_stockout_pct: float = 1.5,
    unfulfilled_conversion: float = 0.70
) -> Dict[str, Any]:
    """
    Model uncaptured gross revenue from inventory stockouts.
    Formula: Lost Orders = Total Demand * (Stockout Rate - Target Stockout) * Unfulfilled Conversion
             Lost Revenue = Lost Orders * AOV
    """
    excess_stockout = max(0.0, stockout_rate_pct - target_stockout_pct) / 100.0
    lost_orders = total_orders_demand * excess_stockout * unfulfilled_conversion
    lost_revenue = lost_orders * avg_order_value

    return {
        "kpi_name": "Stockout Rate",
        "current_stockout_pct": stockout_rate_pct,
        "target_stockout_pct": target_stockout_pct,
        "estimated_lost_orders": round(lost_orders, 0),
        "impact_type": "Lost Revenue Opportunity",
        "base_financial_impact": round(-lost_revenue, 2),
        "low_scenario": round(-lost_revenue * 0.80, 2),
        "high_scenario": round(-lost_revenue * 1.25, 2),
        "formula": "Lost Revenue = Orders Demand * (Excess Stockout %) * Purchase Intent Factor * AOV",
        "assumptions": f"Assumes {unfulfilled_conversion*100:.0f}% of stocked-out customers abandon rather than backorder.",
        "uncertainty_rating": "Moderate uncertainty due to backorder recapture",
    }


def model_turnover_cost_impact(
    total_headcount: int,
    voluntary_turnover_pct: float,
    target_turnover_pct: float = 8.0,
    avg_annual_salary: float = 85_000.0,
    replacement_multiplier: float = 0.50
) -> Dict[str, Any]:
    """
    Model direct and indirect turnover cost (recruitment, onboarding, productivity dip).
    Formula: Excess Separations = Headcount * (Turnover % - Target %)
             Turnover Cost = Excess Separations * (Salary * Multiplier)
    """
    excess_rate = max(0.0, voluntary_turnover_pct - target_turnover_pct) / 100.0
    excess_departures = total_headcount * excess_rate
    cost_per_departure = avg_annual_salary * replacement_multiplier
    total_cost = excess_departures * cost_per_departure

    return {
        "kpi_name": "Employee Turnover",
        "current_turnover_pct": voluntary_turnover_pct,
        "target_turnover_pct": target_turnover_pct,
        "excess_departures_annualized": round(excess_departures, 1),
        "impact_type": "Onboarding & Replacement Expense",
        "base_financial_impact": round(-total_cost, 2),
        "low_scenario": round(-total_cost * 0.75, 2),
        "high_scenario": round(-total_cost * 1.30, 2),
        "formula": "Cost = Headcount * (Turnover % - Target %) * (Annual Salary * Replacement Factor)",
        "assumptions": f"SHRM industry standard replacement multiplier of {replacement_multiplier*100:.0f}% of ${avg_annual_salary:,.0f} salary.",
        "uncertainty_rating": "Estimated industry standard benchmarks",
    }


def model_fulfillment_cost_impact(
    total_orders: int,
    current_cost_per_order: float,
    target_cost_per_order: float
) -> Dict[str, Any]:
    """
    Model operating margin impact from order fulfillment cost variance.
    Formula: OpEx Impact = (Current Cost - Target Cost) * Total Orders
    """
    delta_cost = current_cost_per_order - target_cost_per_order
    opex_impact = delta_cost * total_orders

    return {
        "kpi_name": "Cost per Order",
        "current_cost": current_cost_per_order,
        "target_cost": target_cost_per_order,
        "total_orders": total_orders,
        "impact_type": "Fulfillment OpEx Variance",
        "base_financial_impact": round(-opex_impact, 2),
        "low_scenario": round(-opex_impact * 1.15, 2),
        "high_scenario": round(-opex_impact * 0.85, 2),
        "formula": "Impact = (Current Cost/Order - Target Cost/Order) * Total Orders Fulfilled",
        "assumptions": "Direct operational handling and dispatch costs per order.",
        "uncertainty_rating": "Direct observable variance",
    }
