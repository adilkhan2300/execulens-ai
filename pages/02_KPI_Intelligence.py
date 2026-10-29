"""
ExecuLens AI - Page 2: KPI Intelligence
Operational KPI explorer, departmental comparisons, target deviations, and metadata definitions.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.data_ingestion import get_data_store, filter_datasets
from src.kpi_engine import aggregate_kpi_summary
from src.ui_components import apply_executive_styles, render_page_header

def render():
    apply_executive_styles()
    store = get_data_store()
    fin_df = store.financial_df
    ops_df = store.operational_df
    defs_df = store.kpi_defs_df
    defs_dict = defs_df.set_index("kpi_name").to_dict(orient="index") if defs_df is not None else {}

    render_page_header(
        title="KPI Intelligence Center",
        subtitle="Explore operational KPIs across business units, inspect targets and thresholds, and review formal KPI definitions.",
        badge="Page 02"
    )

    if ops_df is None or ops_df.empty:
        st.warning("Operational data not available.")
        return

    # Filters Row
    col_d, col_s = st.columns(2)
    with col_d:
        depts = ["All"] + sorted(ops_df["department"].unique().tolist())
        selected_dept = st.selectbox("Department Filter", depts, index=0)
    with col_s:
        status_filter = st.selectbox("Status Filter", ["All", "Critical", "Warning", "Healthy"], index=0)

    # Filter operational summary
    summary_df = aggregate_kpi_summary(ops_df, defs_dict)
    if selected_dept != "All":
        summary_df = summary_df[summary_df["department"] == selected_dept]
    if status_filter != "All":
        summary_df = summary_df[summary_df["status"] == status_filter]

    tab_summary, tab_explorer, tab_defs = st.tabs([
        "📋 KPI Health & Target Deviations",
        "📈 Time-Series Deep Dive",
        "📖 KPI Definitions & Metadata"
    ])

    with tab_summary:
        st.markdown(f"#### **Showing {len(summary_df)} Operational Indicators**")
        
        # Display summary dataframe with clean formatting
        display_cols = [
            "department", "kpi_name", "kpi_unit", "current_value",
            "target_value", "target_deviation_pct", "mom_change_pct",
            "status", "sentiment", "business_owner"
        ]
        st.dataframe(
            summary_df[display_cols].sort_values("target_deviation_pct", key=abs, ascending=False),
            use_container_width=True,
            hide_index=True
        )

    with tab_explorer:
        st.markdown("#### **Interactive Operational KPI Trajectory**")
        all_kpis = sorted(ops_df["kpi_name"].unique().tolist())
        chosen_kpi = st.selectbox("Select Operational KPI to Chart", all_kpis, index=0)
        
        kpi_history = ops_df[ops_df["kpi_name"] == chosen_kpi].groupby(["date", "business_unit"])["kpi_value"].mean().reset_index()
        
        meta = defs_dict.get(chosen_kpi, {})
        target_val = meta.get("target_value", 0.0)
        unit = meta.get("unit", "")
        
        fig = px.line(
            kpi_history,
            x="date",
            y="kpi_value",
            color="business_unit",
            markers=True,
            title=f"{chosen_kpi} Monthly History ({unit}) Across Business Units"
        )
        if target_val:
            fig.add_hline(y=target_val, line_dash="dash", line_color="#DC2626", annotation_text=f"Target: {target_val} {unit}")
        fig.update_layout(plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with tab_defs:
        st.markdown("#### **Formal KPI Catalog & Metadata Directory**")
        if defs_df is not None:
            st.dataframe(defs_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    render()
