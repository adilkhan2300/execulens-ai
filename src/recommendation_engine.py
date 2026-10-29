"""
ExecuLens AI - Recommendation & Action Prioritization Engine
Translates analytical findings and adverse KPI movements into prioritized executive actions,
calculating an explainable Priority Score based on Urgency, Financial Impact, Feasibility,
and Evidence Strength.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
from config.settings import ACTION_PRIORITY_WEIGHTS
from src.database import upsert_action, get_all_actions

PRIORITY_SCALE = {"High": 1.0, "Medium": 0.65, "Low": 0.35}
EFFORT_SCALE = {"Low": 1.0, "Medium": 0.70, "High": 0.40}  # Low effort = Higher feasibility
EVIDENCE_SCALE = {"High": 1.0, "Medium": 0.70, "Low": 0.40}

def compute_action_priority_score(
    urgency: str,
    impact_level: str,
    feasibility: str,
    evidence_strength: str
) -> float:
    """
    Transparent Prioritization Score Formula (0-100):
    Score = (w_urg * Urgency + w_imp * Impact + w_feas * Feasibility + w_ev * Evidence) * 100
    """
    w = ACTION_PRIORITY_WEIGHTS
    u = PRIORITY_SCALE.get(urgency, 0.5)
    i = PRIORITY_SCALE.get(impact_level, 0.5)
    f = EFFORT_SCALE.get(feasibility, 0.5)
    e = EVIDENCE_SCALE.get(evidence_strength, 0.5)

    score = (
        w["urgency"] * u +
        w["financial_impact"] * i +
        w["feasibility"] * f +
        w["evidence_strength"] * e
    ) * 100.0

    return round(float(score), 1)


def generate_automated_recommendations(
    adverse_kpis: List[Dict[str, Any]],
    financial_scorecard: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generate prioritized management action proposals derived from detected adverse movements.
    """
    recommendations = []
    today = datetime.now()

    # Domain rule catalog
    catalog = {
        "Stockout Rate": {
            "action": "Activate secondary supplier emergency buffer contracts and review safety stock algorithms",
            "dept": "Supply Chain",
            "owner": "Head of Supply Chain",
            "urgency": "High",
            "impact": "High",
            "effort": "Medium",
            "evidence": "High",
            "success_metric": "Stockout Rate < 2.0%",
            "days_to_target": 45,
        },
        "Sales Conversion Rate": {
            "action": "Deploy focused enterprise pipeline qualification and objection-handling refresher workshops",
            "dept": "Sales",
            "owner": "VP Sales",
            "urgency": "High",
            "impact": "High",
            "effort": "Low",
            "evidence": "High",
            "success_metric": "+0.5% conversion uplift in 60 days",
            "days_to_target": 60,
        },
        "Customer Acquisition Cost": {
            "action": "Trim bottom 20% of paid search keywords and shift budget to account-based syndication",
            "dept": "Marketing",
            "owner": "Chief Marketing Officer",
            "urgency": "Medium",
            "impact": "High",
            "effort": "Low",
            "evidence": "Medium",
            "success_metric": "CAC reduction of $200 per acquired customer",
            "days_to_target": 30,
        },
        "Order Fulfillment Time": {
            "action": "Standardize cross-dock dispatch schedules and balance fulfillment shifts across regional hubs",
            "dept": "Operations",
            "owner": "VP Operations",
            "urgency": "Medium",
            "impact": "Medium",
            "effort": "Medium",
            "evidence": "High",
            "success_metric": "Fulfillment time < 24 hours",
            "days_to_target": 45,
        },
        "Employee Turnover": {
            "action": "Conduct immediate retention reviews and adjust compensation for critical operational talent",
            "dept": "Human Resources",
            "owner": "Chief People Officer",
            "urgency": "High",
            "impact": "High",
            "effort": "Medium",
            "evidence": "Medium",
            "success_metric": "Voluntary turnover < 8.5%",
            "days_to_target": 90,
        },
        "Customer Satisfaction Score": {
            "action": "Implement rapid escalation path for SLA breaches and train support agents on first-contact resolution",
            "dept": "Customer Service",
            "owner": "VP Customer Experience",
            "urgency": "Medium",
            "impact": "Medium",
            "effort": "Low",
            "evidence": "Medium",
            "success_metric": "CSAT > 88.0",
            "days_to_target": 30,
        },
    }

    seen_kpis = set()
    rec_counter = 1

    for item in adverse_kpis:
        kpi_name = item.get("kpi_name")
        if not kpi_name or kpi_name in seen_kpis:
            continue

        template = catalog.get(kpi_name)
        if not template:
            # Generic template
            dept = item.get("department", "Operations")
            template = {
                "action": f"Conduct operational deep-dive and stabilization review for {kpi_name}",
                "dept": dept,
                "owner": f"Head of {dept}",
                "urgency": "Medium",
                "impact": "Medium",
                "effort": "Medium",
                "evidence": "Medium",
                "success_metric": f"Return {kpi_name} to target",
                "days_to_target": 60,
            }

        seen_kpis.add(kpi_name)
        p_score = compute_action_priority_score(
            template["urgency"],
            template["impact"],
            template["effort"],
            template["evidence"]
        )

        target_date = (today + timedelta(days=template["days_to_target"])).strftime("%Y-%m-%d")
        action_id = f"REC-{today.strftime('%Y%m')}-{rec_counter:03d}"
        rec_counter += 1

        recommendations.append({
            "action_id": action_id,
            "date_created": today.strftime("%Y-%m-%d"),
            "problem": f"{kpi_name} deviated by {item.get('pct_delta', item.get('target_deviation_pct', 0)):+.1f}%",
            "related_kpi": kpi_name,
            "related_financial_outcome": item.get("linked_outcome", "Operating Profit"),
            "action_description": template["action"],
            "owner": template["owner"],
            "department": template["dept"],
            "urgency": template["urgency"],
            "impact": template["impact"],
            "effort": template["effort"],
            "evidence_strength": template["evidence"],
            "priority_score": p_score,
            "status": "Proposed",
            "target_date": target_date,
            "success_metric": template["success_metric"],
            "review_date": target_date,
        })

    # Sort by priority score descending
    recommendations.sort(key=lambda x: x["priority_score"], reverse=True)
    return recommendations
