"""
ExecuLens AI - Page 10: Data Center & Ingestion Hub
CSV and Excel uploads, column mappings, data validation reports, and synthetic dataset controls.
"""

import streamlit as st
import pandas as pd
import json
from src.data_ingestion import get_data_store, process_uploaded_file, load_default_synthetic_data
from src.synthetic_generator import save_synthetic_datasets
from src.ui_components import apply_executive_styles, render_page_header

def render():
    apply_executive_styles()
    store = get_data_store()

    render_page_header(
        title="Enterprise Data Ingestion & Governance Center",
        subtitle="Upload custom CSV/Excel business datasets, review validation health reports, or regenerate demonstration data.",
        badge="Page 10"
    )

    tab_upload, tab_validation, tab_synthetic = st.tabs([
        "📤 Dataset Upload & Column Mapping",
        "🩺 Data Quality & Validation Reports",
        "⚙️ Synthetic Demonstration Controls"
    ])

    with tab_upload:
        st.markdown("#### **Upload Corporate Business Datasets (CSV or Excel)**")
        st.caption("Upload company data to run live diagnostics. The system never silently alters raw inputs.")

        dataset_type = st.selectbox(
            "Select Target Dataset Type",
            [
                "financial_performance",
                "operational_kpis",
                "kpi_definitions",
                "business_events",
                "management_actions"
            ]
        )

        uploaded_file = st.file_uploader(f"Choose a CSV or Excel file for '{dataset_type}'", type=["csv", "xlsx", "xls"])

        if uploaded_file is not None:
            # Preview uploaded file
            try:
                if uploaded_file.name.endswith(".xlsx") or uploaded_file.name.endswith(".xls"):
                    df_preview = pd.read_excel(uploaded_file)
                else:
                    df_preview = pd.read_csv(uploaded_file)
                
                st.markdown(f"##### Previewing `{uploaded_file.name}` ({len(df_preview)} rows, {len(df_preview.columns)} columns)")
                st.dataframe(df_preview.head(5), use_container_width=True)

                if st.button("Validate & Ingest File"):
                    uploaded_file.seek(0)
                    success, msg, df_ingested, report = process_uploaded_file(uploaded_file, dataset_type)
                    if success:
                        st.success(msg)
                        if report and report.warnings:
                            st.warning(f"Ingested with {len(report.warnings)} warnings: {report.warnings}")
                    else:
                        st.error(msg)
            except Exception as e:
                st.error(f"Error reading uploaded file: {e}")

    with tab_validation:
        st.markdown("#### **Active Dataset Health & Validation Reports**")
        
        for name, report in store.validation_reports.items():
            status_color = "🟢 PASS" if report.status == "PASS" else ("🟡 WARNING" if report.status == "WARNING" else "🔴 FAIL")
            with st.expander(f"**Dataset: `{name}`** — *Status: {status_color}*"):
                st.json(report.to_dict())

    with tab_synthetic:
        st.markdown("#### **Synthetic Demonstration Dataset Controls**")
        st.write("""
        The synthetic demonstration generator creates 24 months of monthly data for 4 business units, 5 regions, 6 departments, and 34 operational KPIs with embedded realistic business shocks, lead-lag effects, and seasonality.
        """)

        c_seed, c_btn = st.columns([1, 2])
        with c_seed:
            custom_seed = st.number_input("Deterministic Random Seed", value=42, step=1)
        with c_btn:
            st.write("")
            st.write("")
            if st.button("Regenerate & Reload Synthetic Data", type="primary"):
                with st.spinner("Regenerating synthetic records..."):
                    save_synthetic_datasets()
                    load_default_synthetic_data()
                    st.success("Fresh synthetic datasets generated and reloaded successfully into memory!")
                    st.rerun()

if __name__ == "__main__":
    render()
