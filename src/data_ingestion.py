"""
ExecuLens AI - Data Ingestion & Harmonization
Loads synthetic or uploaded business datasets, applies column mappings,
standardizes date intervals, and prepares unified analytical data structures.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from config.settings import (
    SYNTHETIC_DATA_DIR,
    UPLOADS_DATA_DIR,
)
from src.data_validation import (
    validate_financial_data,
    validate_operational_data,
    validate_kpi_definitions,
    ValidationReport
)
from src.database import log_audit_event

class DataStore:
    """In-memory singleton storage for active session datasets and validation status."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataStore, cls).__new__(cls)
            cls._instance.financial_df: Optional[pd.DataFrame] = None
            cls._instance.operational_df: Optional[pd.DataFrame] = None
            cls._instance.kpi_defs_df: Optional[pd.DataFrame] = None
            cls._instance.events_df: Optional[pd.DataFrame] = None
            cls._instance.actions_df: Optional[pd.DataFrame] = None
            cls._instance.validation_reports: Dict[str, ValidationReport] = {}
            cls._instance.source_type: str = "synthetic"
        return cls._instance

def get_data_store() -> DataStore:
    """Retrieve the global DataStore instance."""
    store = DataStore()
    if store.financial_df is None:
        load_default_synthetic_data()
    return store

def load_default_synthetic_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load default synthetic CSV files into the DataStore."""
    store = DataStore()
    
    fin_path = SYNTHETIC_DATA_DIR / "financial_performance.csv"
    ops_path = SYNTHETIC_DATA_DIR / "operational_kpis.csv"
    defs_path = SYNTHETIC_DATA_DIR / "kpi_definitions.csv"
    events_path = SYNTHETIC_DATA_DIR / "business_events.csv"
    actions_path = SYNTHETIC_DATA_DIR / "management_actions.csv"
    
    # Check if files exist; if not, generate them
    if not (fin_path.exists() and ops_path.exists() and defs_path.exists()):
        from src.synthetic_generator import save_synthetic_datasets
        save_synthetic_datasets()
        
    store.financial_df = pd.read_csv(fin_path)
    store.operational_df = pd.read_csv(ops_path)
    store.kpi_defs_df = pd.read_csv(defs_path)
    store.events_df = pd.read_csv(events_path) if events_path.exists() else pd.DataFrame()
    store.actions_df = pd.read_csv(actions_path) if actions_path.exists() else pd.DataFrame()
    
    # Run and cache validations
    store.validation_reports["financial_performance"] = validate_financial_data(store.financial_df)
    store.validation_reports["operational_kpis"] = validate_operational_data(store.operational_df)
    store.validation_reports["kpi_definitions"] = validate_kpi_definitions(store.kpi_defs_df)
    store.source_type = "synthetic"
    
    log_audit_event("LOAD_SYNTHETIC_DATA", "Default synthetic datasets loaded successfully")
    return store.financial_df, store.operational_df, store.kpi_defs_df, store.events_df, store.actions_df

def process_uploaded_file(
    file_obj,
    dataset_type: str,
    column_mapping: Optional[Dict[str, str]] = None
) -> Tuple[bool, str, Optional[pd.DataFrame], Optional[ValidationReport]]:
    """
    Ingest, remap, and validate an uploaded CSV or Excel file.
    """
    try:
        filename = getattr(file_obj, "name", "uploaded_file")
        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            df = pd.read_excel(file_obj)
        else:
            df = pd.read_csv(file_obj)
            
        if column_mapping:
            df = df.rename(columns=column_mapping)
            
        # Clean string columns
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip()
            
        store = DataStore()
        report = None
        
        if dataset_type == "financial_performance":
            report = validate_financial_data(df)
            if report.status != "FAIL":
                store.financial_df = df
                store.validation_reports["financial_performance"] = report
                store.source_type = "uploaded"
        elif dataset_type == "operational_kpis":
            report = validate_operational_data(df)
            if report.status != "FAIL":
                store.operational_df = df
                store.validation_reports["operational_kpis"] = report
                store.source_type = "uploaded"
        elif dataset_type == "kpi_definitions":
            report = validate_kpi_definitions(df)
            if report.status != "FAIL":
                store.kpi_defs_df = df
                store.validation_reports["kpi_definitions"] = report
        elif dataset_type == "business_events":
            store.events_df = df
        elif dataset_type == "management_actions":
            store.actions_df = df
        else:
            return False, f"Unknown dataset type: {dataset_type}", None, None
            
        log_audit_event("UPLOAD_DATASET", f"Uploaded {filename} as {dataset_type}", {"rows": len(df)})
        return True, f"Successfully processed {filename} ({len(df)} rows)", df, report
        
    except Exception as e:
        return False, f"Failed to ingest file: {str(e)}", None, None

def get_kpi_metadata_dict() -> Dict[str, Dict[str, Any]]:
    """Return KPI definitions mapped by KPI name for fast O(1) attribute lookup."""
    store = get_data_store()
    if store.kpi_defs_df is None or store.kpi_defs_df.empty:
        return {}
    return store.kpi_defs_df.set_index("kpi_name").to_dict(orient="index")

def filter_datasets(
    financial_df: pd.DataFrame,
    operational_df: pd.DataFrame,
    date_range: Optional[Tuple[str, str]] = None,
    business_units: Optional[List[str]] = None,
    regions: Optional[List[str]] = None,
    departments: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Apply unified executive filters across financial and operational datasets.
    """
    f_df = financial_df.copy()
    o_df = operational_df.copy()
    
    if date_range and len(date_range) == 2:
        start_d, end_d = str(date_range[0]), str(date_range[1])
        f_df = f_df[(f_df["date"] >= start_d) & (f_df["date"] <= end_d)]
        o_df = o_df[(o_df["date"] >= start_d) & (o_df["date"] <= end_d)]
        
    if business_units and "All" not in business_units:
        f_df = f_df[f_df["business_unit"].isin(business_units)]
        o_df = o_df[o_df["business_unit"].isin(business_units)]
        
    if regions and "All" not in regions:
        f_df = f_df[f_df["region"].isin(regions)]
        o_df = o_df[o_df["region"].isin(regions)]
        
    if departments and "All" not in departments and "department" in o_df.columns:
        o_df = o_df[o_df["department"].isin(departments)]
        
    return f_df, o_df
