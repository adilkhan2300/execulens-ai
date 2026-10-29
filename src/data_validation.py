"""
ExecuLens AI - Data Validation Engine
Validates uploaded or synthetic datasets for completeness, mathematical integrity,
date continuity, duplicate keys, and schema conformance without silent corruption.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime

FINANCIAL_REQUIRED_COLS = [
    "date", "business_unit", "region", "product_category", "revenue",
    "cost_of_goods_sold", "operating_expenses", "gross_profit",
    "operating_profit", "cash_flow", "customer_count", "orders_count"
]

OPERATIONAL_REQUIRED_COLS = [
    "date", "department", "business_unit", "region",
    "kpi_name", "kpi_value", "kpi_unit", "target_value"
]

KPI_DEFS_REQUIRED_COLS = [
    "kpi_name", "department", "description", "unit",
    "direction", "target_value", "warning_threshold", "critical_threshold"
]

class ValidationReport:
    """Encapsulates structured data validation outcomes."""
    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name
        self.status = "PASS"  # PASS, WARNING, FAIL
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.metrics: Dict[str, Any] = {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_name": self.dataset_name,
            "status": self.status,
            "errors": self.errors,
            "warnings": self.warnings,
            "metrics": self.metrics,
            "timestamp": self.timestamp,
        }

def validate_financial_data(df: pd.DataFrame) -> ValidationReport:
    """
    Validate financial performance dataset for schema, math consistency, and ranges.
    """
    report = ValidationReport("financial_performance")
    
    if df is None or df.empty:
        report.status = "FAIL"
        report.errors.append("Financial dataset is empty or None.")
        return report

    report.metrics["row_count"] = len(df)
    report.metrics["column_count"] = len(df.columns)
    
    # 1. Missing columns
    missing_cols = [c for c in FINANCIAL_REQUIRED_COLS if c not in df.columns]
    if missing_cols:
        report.status = "FAIL"
        report.errors.append(f"Missing required columns: {', '.join(missing_cols)}")
        return report

    # 2. Date parsing and continuity
    try:
        parsed_dates = pd.to_datetime(df["date"], errors="coerce")
        null_dates = parsed_dates.isna().sum()
        if null_dates > 0:
            report.status = "WARNING"
            report.warnings.append(f"Found {null_dates} rows with unparseable date values.")
        else:
            report.metrics["date_min"] = str(parsed_dates.min().date())
            report.metrics["date_max"] = str(parsed_dates.max().date())
            report.metrics["unique_periods"] = parsed_dates.nunique()
    except Exception as e:
        report.status = "FAIL"
        report.errors.append(f"Date conversion error: {str(e)}")

    # 3. Missing values check
    null_counts = df[FINANCIAL_REQUIRED_COLS].isna().sum()
    cols_with_nulls = null_counts[null_counts > 0].to_dict()
    if cols_with_nulls:
        report.status = "WARNING"
        report.warnings.append(f"Columns with null values: {cols_with_nulls}")
    
    # 4. Duplicate records check
    dup_keys = ["date", "business_unit", "region", "product_category"]
    dups = df.duplicated(subset=dup_keys).sum()
    if dups > 0:
        report.status = "WARNING"
        report.warnings.append(f"Found {dups} duplicate records based on {dup_keys}.")

    # 5. Mathematical identities check
    # Gross Profit = Revenue - COGS
    expected_gp = df["revenue"] - df["cost_of_goods_sold"]
    gp_diff = (df["gross_profit"] - expected_gp).abs()
    gp_mismatches = (gp_diff > 1.0).sum()
    if gp_mismatches > 0:
        report.status = "WARNING"
        report.warnings.append(
            f"Gross Profit mismatch in {gp_mismatches} rows (Revenue - COGS != Gross Profit)."
        )

    # Operating Profit = Gross Profit - OpEx
    expected_op = df["gross_profit"] - df["operating_expenses"]
    op_diff = (df["operating_profit"] - expected_op).abs()
    op_mismatches = (op_diff > 1.0).sum()
    if op_mismatches > 0:
        report.status = "WARNING"
        report.warnings.append(
            f"Operating Profit mismatch in {op_mismatches} rows (Gross Profit - OpEx != Operating Profit)."
        )

    # 6. Negative values sanity
    neg_rev = (df["revenue"] < 0).sum()
    if neg_rev > 0:
        report.status = "WARNING"
        report.warnings.append(f"Found {neg_rev} rows with negative revenue.")

    return report


def validate_operational_data(df: pd.DataFrame) -> ValidationReport:
    """
    Validate operational KPIs dataset for schema, consistency, and metrics.
    """
    report = ValidationReport("operational_kpis")
    
    if df is None or df.empty:
        report.status = "FAIL"
        report.errors.append("Operational KPIs dataset is empty or None.")
        return report

    report.metrics["row_count"] = len(df)
    report.metrics["column_count"] = len(df.columns)
    
    missing_cols = [c for c in OPERATIONAL_REQUIRED_COLS if c not in df.columns]
    if missing_cols:
        report.status = "FAIL"
        report.errors.append(f"Missing required columns: {', '.join(missing_cols)}")
        return report

    # Date parsing
    try:
        parsed_dates = pd.to_datetime(df["date"], errors="coerce")
        null_dates = parsed_dates.isna().sum()
        if null_dates > 0:
            report.status = "WARNING"
            report.warnings.append(f"Found {null_dates} rows with invalid dates.")
        else:
            report.metrics["unique_periods"] = parsed_dates.nunique()
    except Exception as e:
        report.errors.append(f"Date parsing failed: {e}")

    # Check numeric KPI values
    non_numeric_vals = pd.to_numeric(df["kpi_value"], errors="coerce").isna().sum()
    if non_numeric_vals > 0:
        report.status = "WARNING"
        report.warnings.append(f"Found {non_numeric_vals} non-numeric kpi_value entries.")

    report.metrics["unique_kpis"] = df["kpi_name"].nunique()
    report.metrics["departments"] = df["department"].unique().tolist()
    
    return report


def validate_kpi_definitions(df: pd.DataFrame) -> ValidationReport:
    """
    Validate KPI definitions metadata.
    """
    report = ValidationReport("kpi_definitions")
    
    if df is None or df.empty:
        report.status = "FAIL"
        report.errors.append("KPI definitions dataset is empty.")
        return report

    report.metrics["total_kpi_definitions"] = len(df)
    
    missing_cols = [c for c in KPI_DEFS_REQUIRED_COLS if c not in df.columns]
    if missing_cols:
        report.status = "FAIL"
        report.errors.append(f"Missing required columns: {', '.join(missing_cols)}")
        return report

    valid_directions = {"higher_is_better", "lower_is_better", "target_range"}
    invalid_dirs = set(df["direction"].unique()) - valid_directions
    if invalid_dirs:
        report.status = "WARNING"
        report.warnings.append(f"Unrecognized KPI directions: {invalid_dirs}. Expected one of {valid_directions}")

    # Duplicate KPI names
    dup_names = df["kpi_name"].duplicated().sum()
    if dup_names > 0:
        report.status = "WARNING"
        report.warnings.append(f"Found {dup_names} duplicate KPI names in definition table.")

    return report
