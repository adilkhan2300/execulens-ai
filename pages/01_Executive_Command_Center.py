"""
ExecuLens AI - Page 1: Executive Command Center
Consolidated executive view: performance cards, trend charts, budget variance, and executive alerts.
"""

import streamlit as st
import pandas as pd
from config.settings import format_currency, format_percentage
from src.data_ingestion import get_data_store, filter_datasets
from src.kpi_engine import compute_executive_scorecard
from src.anomaly_detection import detect_kpi_anomalies, detect_co_occurring_risks
from src.ui_components import (
    apply_executive_styles,
    render_page_header,
    render_metric_card,
    create_revenue_profit_trend_chart
)
from src.reporting import generate_pdf_executive_report
from src.driver_analysis import build_aligned_analysis_matrix, analyze_kpi_correlations
from src.root_cause import investigate_performance_event
from src.recommendation_engine import generate_automated_recommendations

def render():
    apply_executive_styles()
    store = get_data_store()
    fin_df = store.financial_df
    ops_df = store.operational_df
    defs_dict = store.kpi_defs_df.set_index("kpi_name").to_dict(orient="index") if store.kpi_defs_df is not None else {}
    events_df = store.events_df

    render_page_header(
        title="Executive Command Center",
        subtitle="High-level corporate health, KPI performance scorecards, active alerts, and strategic trends.",
        badge="Page 01"
    )

    if fin_df is None or fin_df.empty:
        st.error("Financial data unavailable. Please initialize synthetic data or upload datasets in Data Center.")
        return

    # Top Filters
    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
        dates = sorted(fin_df["date"].unique())
        selected_period = st.selectbox("Current Period", dates, index=len(dates)-1)
    with c_f2:
        bus = ["All"] + sorted(fin_df["business_unit"].unique().tolist())
        selected_bu = st.selectbox("Business Unit", bus, index=0)
    with c_f3:
        regs = ["All"] + sorted(fin_df["region"].unique().tolist())
        selected_reg = st.selectbox("Region", regs, index=0)

    # Filter data
    f_fin, f_ops = filter_datasets(
        fin_df, ops_df,
        business_units=[selected_bu] if selected_bu != "All" else None,
        regions=[selected_reg] if selected_reg != "All" else None
    )

    # Scorecard
    scorecard = compute_executive_scorecard(f_fin)
    rev_info = scorecard.get("revenue", {})
    op_info = scorecard.get("operating_profit", {})
    margin_info = scorecard.get("operating_margin", {})
    cf_info = scorecard.get("cash_flow", {})

    # Top KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_metric_card(
            "Total Revenue",
            format_currency(rev_info.get("value", 0)),
            rev_info.get("change_pct", 0),
            rev_info.get("favorable", True),
            target_str=format_currency(rev_info.get("target", 0))
        )
    with k2:
        render_metric_card(
            "Operating Profit",
            format_currency(op_info.get("value", 0)),
            op_info.get("change_pct", 0),
            op_info.get("favorable", True),
            target_str=format_currency(op_info.get("target", 0))
        )
    with k3:
        render_metric_card(
            "Operating Margin",
            f"{margin_info.get('value', 0):.1f}%",
            margin_info.get("change_pts", 0),
            margin_info.get("favorable", True),
            target_str="18.5%"
        )
    with k4:
        render_metric_card(
            "Operating Cash Flow",
            format_currency(cf_info.get("value", 0)),
            cf_info.get("change_pct", 0),
            cf_info.get("favorable", True),
            target_str="Stable"
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Tabs for Visuals, Alerts, and Summary
    tab_overview, tab_alerts, tab_export = st.tabs(["📊 Performance Trends", "🚨 Executive Alerts", "📄 PDF Export"])

    with tab_overview:
        fig_trend = create_revenue_profit_trend_chart(f_fin)
        st.plotly_chart(fig_trend, use_container_width=True)

    with tab_alerts:
        st.markdown("#### **Active Operational & Financial Threshold Alerts**")
        alerts = detect_kpi_anomalies(f_ops, defs_dict, current_period=selected_period)
        co_risks = detect_co_occurring_risks(alerts)

        if co_risks:
            st.error(f"⚠️ **Cluster Risk Alert:** Found {len(co_risks)} co-occurring indicator risk cluster(s):")
            for cr in co_risks:
                st.markdown(f"- **{cr['business_unit']}**: {cr['description']} (Affected: *{', '.join(cr['kpis'])}*)")

        if not alerts:
            st.success("✅ No operational KPIs breached warning or critical thresholds in this observation period.")
        else:
            df_alert = pd.DataFrame(alerts)
            st.dataframe(
                df_alert[[
                    "severity", "kpi_name", "department", "business_unit",
                    "current_value", "target_value", "unit", "threshold_breach",
                    "potential_business_significance"
                ]],
                use_container_width=True,
                hide_index=True
            )

    with tab_export:
        st.markdown("#### **Generate & Download Official Executive PDF Briefing**")
        st.write("Generate a publication-grade PDF containing executive scorecards, key driver correlations, root-cause findings, and management actions.")
        
        if st.button("Generate Downloadable PDF Report", type="primary"):
            matrix_df, kpi_cols, _ = build_aligned_analysis_matrix(f_fin, f_ops)
            drivers = analyze_kpi_correlations(matrix_df, "operating_profit", kpi_cols, defs_dict)
            sorted_dates = sorted(f_fin["date"].unique())
            p1 = sorted_dates[-2] if len(sorted_dates) > 1 else sorted_dates[0]
            p2 = sorted_dates[-1]
            rc = investigate_performance_event(f_fin, f_ops, events_df, defs_dict, p1, p2)
            recs = generate_automated_recommendations(rc.get("adverse_kpis", []), scorecard)
            
            pdf_bytes = generate_pdf_executive_report(scorecard, drivers.to_dict(orient="records"), rc.get("hypotheses", []), recs)
            st.download_button(
                label="📥 Click here to save PDF Document",
                data=pdf_bytes,
                file_name=f"ExecuLens_Executive_Report_{selected_period}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

if __name__ == "__main__":
    render()
