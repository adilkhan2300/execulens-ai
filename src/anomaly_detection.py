"""
ExecuLens AI - Anomaly Detection & Executive Alert Engine
Identifies statistical outliers (Z-score, IQR), threshold breaches (Warning/Critical),
performance declines, and multi-indicator risk co-occurrences.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

def detect_kpi_anomalies(
    operational_df: pd.DataFrame,
    kpi_defs_dict: Dict[str, Dict[str, Any]],
    z_threshold: float = 2.0,
    current_period: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Detect KPI threshold breaches and statistical anomalies for the current or selected period.
    """
    if operational_df.empty:
        return []

    alerts = []
    curr_date = current_period or operational_df["date"].max()
    curr_df = operational_df[operational_df["date"] == curr_date]

    # Group by KPI to compute historical baseline stats
    hist_stats = operational_df.groupby("kpi_name")["kpi_value"].agg(["mean", "std"]).to_dict(orient="index")

    for _, row in curr_df.iterrows():
        kpi_name = row["kpi_name"]
        val = float(row["kpi_value"])
        unit = row["kpi_unit"]
        bu = row["business_unit"]
        region = row["region"]
        dept = row["department"]

        meta = kpi_defs_dict.get(kpi_name, {})
        target = meta.get("target_value", val)
        warn_th = meta.get("warning_threshold")
        crit_th = meta.get("critical_threshold")
        direction = meta.get("direction", "higher_is_better")
        outcome_link = meta.get("linked_financial_outcome", "revenue")

        # 1. Threshold breach check
        breach_level = None
        if direction == "higher_is_better":
            if crit_th is not None and val <= crit_th:
                breach_level = "Critical"
            elif warn_th is not None and val <= warn_th:
                breach_level = "Warning"
        elif direction == "lower_is_better":
            if crit_th is not None and val >= crit_th:
                breach_level = "Critical"
            elif warn_th is not None and val >= warn_th:
                breach_level = "Warning"
        elif direction == "target_range":
            if target != 0:
                dev = abs((val - target) / target)
                if dev > 0.25:
                    breach_level = "Critical"
                elif dev > 0.15:
                    breach_level = "Warning"

        # 2. Statistical Z-Score outlier check
        kpi_stat = hist_stats.get(kpi_name, {})
        mean_v = kpi_stat.get("mean", val)
        std_v = kpi_stat.get("std", 1.0)
        z_score = ((val - mean_v) / std_v) if (std_v and not np.isnan(std_v) and std_v > 0) else 0.0

        is_z_anomaly = abs(z_score) >= z_threshold

        if breach_level or is_z_anomaly:
            severity = "High" if (breach_level == "Critical" or abs(z_score) >= 2.5) else "Medium"
            
            # Contextual business significance explanation
            significance = f"Movement in {kpi_name} directly impacts {outcome_link}."
            if is_z_anomaly:
                significance += f" Historical Z-score of {z_score:+.1f} indicates an unusual {abs(z_score):.1f}σ deviation from 24-month mean."

            alerts.append({
                "period": curr_date,
                "kpi_name": kpi_name,
                "department": dept,
                "business_unit": bu,
                "region": region,
                "current_value": val,
                "target_value": target,
                "unit": unit,
                "threshold_breach": breach_level or "Statistical Anomaly",
                "z_score": round(float(z_score), 2),
                "severity": severity,
                "potential_business_significance": significance,
                "linked_outcome": outcome_link,
            })

    # Sort alerts by High severity first
    alerts.sort(key=lambda x: 0 if x["severity"] == "High" else 1)
    return alerts


def detect_co_occurring_risks(alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identify clusters of adverse indicators occurring simultaneously within the same business unit.
    """
    if not alerts:
        return []

    df_alerts = pd.DataFrame(alerts)
    co_occurrences = []

    grouped = df_alerts.groupby(["period", "business_unit"])
    for (period, bu), group in grouped:
        if len(group) >= 2:
            kpis_involved = group["kpi_name"].unique().tolist()
            depts_involved = group["department"].unique().tolist()
            co_occurrences.append({
                "period": period,
                "business_unit": bu,
                "adverse_kpi_count": len(group),
                "kpis": kpis_involved,
                "departments": depts_involved,
                "composite_risk_level": "Elevated Cluster Risk",
                "description": f"{len(group)} anomalous KPI movements detected across {', '.join(depts_involved)} in {bu}."
            })

    return co_occurrences
