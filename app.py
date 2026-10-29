"""
ExecuLens AI - Executive Decision Intelligence & Business Performance Insights
Main Streamlit Application Entrypoint
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Streamlit Page Configuration - Executive Theme
st.set_page_config(
    page_title="ExecuLens AI — Executive Decision Intelligence",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

from config.settings import (
    APP_NAME,
    APP_SUBTITLE,
    APP_VERSION,
    DEFAULT_CURRENCY,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    format_currency,
    format_percentage
)
from src.data_ingestion import get_data_store, filter_datasets
from src.kpi_engine import compute_executive_scorecard
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

def main():
    apply_executive_styles()
    
    # Initialize Data Store
    store = get_data_store()
    fin_df = store.financial_df
    ops_df = store.operational_df
    defs_dict = store.kpi_defs_df.set_index("kpi_name").to_dict(orient="index") if store.kpi_defs_df is not None else {}
    events_df = store.events_df

    # Sidebar Navigation & Corporate Controls
    with st.sidebar:
        st.markdown(f"### 💼 **{APP_NAME}**")
        st.caption(f"v{APP_VERSION} • Decision Intelligence")
        st.markdown("---")
        
        st.markdown("#### 🎯 **Global Filters**")
        
        # Date Filter
        all_dates = sorted(fin_df["date"].unique()) if fin_df is not None and not fin_df.empty else []
        if len(all_dates) >= 2:
            selected_date_range = st.select_slider(
                "Observation Window",
                options=all_dates,
                value=(all_dates[0], all_dates[-1])
            )
        else:
            selected_date_range = None

        # Business Unit Filter
        bus = ["All"] + sorted(fin_df["business_unit"].unique().tolist()) if fin_df is not None else ["All"]
        selected_bu = st.selectbox("Business Unit", bus, index=0)

        # Region Filter
        regs = ["All"] + sorted(fin_df["region"].unique().tolist()) if fin_df is not None else ["All"]
        selected_reg = st.selectbox("Region", regs, index=0)

        # Currency Setting
        currency_sym = st.selectbox("Display Currency", ["$", "€", "£", "₹", "¥"], index=0)

        st.markdown("---")
        # System & AI Status
        ai_status = "🟢 OpenAI API Active" if OPENAI_API_KEY else "🔵 Deterministic Zero-API Mode"
        st.caption(f"**AI Engine:** {ai_status}")
        st.caption(f"**Data Mode:** {store.source_type.title()} Data")
        
        # Download Briefing PDF quick link
        if st.button("📄 Quick Export PDF Report", use_container_width=True):
            scorecard = compute_executive_scorecard(fin_df)
            matrix_df, kpi_cols, _ = build_aligned_analysis_matrix(fin_df, ops_df)
            drivers = analyze_kpi_correlations(matrix_df, "operating_profit", kpi_cols, defs_dict)
            sorted_dates = sorted(fin_df["date"].unique())
            rc = investigate_performance_event(fin_df, ops_df, events_df, defs_dict, sorted_dates[-2], sorted_dates[-1])
            recs = generate_automated_recommendations(rc.get("adverse_kpis", []), scorecard)
            
            pdf_data = generate_pdf_executive_report(scorecard, drivers.to_dict(orient="records"), rc.get("hypotheses", []), recs)
            st.download_button(
                label="📥 Click to Download PDF",
                data=pdf_data,
                file_name=f"ExecuLens_Briefing_{scorecard.get('current_period', 'latest')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    # Filter data according to sidebar
    filtered_fin, filtered_ops = filter_datasets(
        fin_df, ops_df,
        date_range=selected_date_range,
        business_units=[selected_bu] if selected_bu != "All" else None,
        regions=[selected_reg] if selected_reg != "All" else None
    )

    # Render Header
    render_page_header(
        title="Executive Command Center",
        subtitle=f"Consolidated multi-departmental business performance for {selected_bu} ({selected_reg}). Core question: What is driving performance, what changed, and what should management do next?",
        badge="Executive Overview"
    )

    if filtered_fin.empty:
        st.warning("No records match the selected filter criteria. Please broaden filters in the sidebar.")
        return

    # Compute scorecard
    scorecard = compute_executive_scorecard(filtered_fin)

    # 1. Top-Level Metric Scorecard Row
    rev_info = scorecard.get("revenue", {})
    op_info = scorecard.get("operating_profit", {})
    margin_info = scorecard.get("operating_margin", {})
    cf_info = scorecard.get("cash_flow", {})

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card(
            title="Total Revenue",
            value_str=format_currency(rev_info.get("value", 0), currency_sym),
            change_pct=rev_info.get("change_pct", 0),
            favorable=rev_info.get("favorable", True),
            target_str=format_currency(rev_info.get("target", 0), currency_sym)
        )
    with c2:
        render_metric_card(
            title="Operating Profit",
            value_str=format_currency(op_info.get("value", 0), currency_sym),
            change_pct=op_info.get("change_pct", 0),
            favorable=op_info.get("favorable", True),
            target_str=format_currency(op_info.get("target", 0), currency_sym)
        )
    with c3:
        render_metric_card(
            title="Operating Margin",
            value_str=f"{margin_info.get('value', 0):.1f}%",
            change_pct=margin_info.get("change_pts", 0),
            favorable=margin_info.get("favorable", True),
            target_str="18.5%"
        )
    with c4:
        render_metric_card(
            title="Executive Performance Score",
            value_str=f"{scorecard.get('performance_score', 0)}/100",
            change_pct=None,
            favorable=scorecard.get("performance_score", 0) >= 70,
            target_str="85.0"
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 2. Main Visualizations Row
    col_chart, col_side = st.columns([2, 1])

    with col_chart:
        fig_trend = create_revenue_profit_trend_chart(filtered_fin)
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_side:
        st.markdown("#### ⚡ **Executive Performance Insights**")
        st.markdown(f"""
        - **Reporting Period:** {scorecard.get('current_period')}
        - **Revenue Growth:** {format_percentage(rev_info.get('change_pct', 0), show_sign=True)} vs prior month.
        - **Budget Target Achievement:** {scorecard.get('budget_achievement', 0):.1f}% of commercial target.
        - **Operating Cash Flow:** {format_currency(cf_info.get('value', 0), currency_sym)}.
        - **COGS Ratio:** {scorecard.get('cogs', {}).get('pct_of_rev', 0):.1f}% of revenue.
        - **OpEx Ratio:** {scorecard.get('opex', {}).get('pct_of_rev', 0):.1f}% of revenue.
        """)
        
        st.info("💡 **Quick Navigation:** Use the left sidebar to explore driver regressions, root-cause drilldowns, scenario simulations, or AI briefings.")

    # 3. Departmental & Regional Heatmap Overview
    st.markdown("---")
    st.markdown("### 🏢 **Business Unit & Regional Breakdown**")
    
    tab_bu, tab_reg = st.tabs(["Business Units", "Regions"])
    
    with tab_bu:
        bu_summary = filtered_fin[filtered_fin["date"] == scorecard.get("current_period")].groupby("business_unit").agg(
            Revenue=("revenue", "sum"),
            Cost_of_Goods=("cost_of_goods_sold", "sum"),
            Operating_Profit=("operating_profit", "sum")
        ).reset_index()
        bu_summary["Operating Margin (%)"] = (bu_summary["Operating_Profit"] / bu_summary["Revenue"] * 100.0).round(1)
        bu_summary["Revenue"] = bu_summary["Revenue"].apply(lambda v: format_currency(v, currency_sym))
        bu_summary["Cost_of_Goods"] = bu_summary["Cost_of_Goods"].apply(lambda v: format_currency(v, currency_sym))
        bu_summary["Operating_Profit"] = bu_summary["Operating_Profit"].apply(lambda v: format_currency(v, currency_sym))
        st.dataframe(bu_summary, use_container_width=True, hide_index=True)

    with tab_reg:
        reg_summary = filtered_fin[filtered_fin["date"] == scorecard.get("current_period")].groupby("region").agg(
            Revenue=("revenue", "sum"),
            Operating_Profit=("operating_profit", "sum")
        ).reset_index()
        reg_summary["Margin (%)"] = (reg_summary["Operating_Profit"] / reg_summary["Revenue"] * 100.0).round(1)
        reg_summary["Revenue"] = reg_summary["Revenue"].apply(lambda v: format_currency(v, currency_sym))
        reg_summary["Operating_Profit"] = reg_summary["Operating_Profit"].apply(lambda v: format_currency(v, currency_sym))
        st.dataframe(reg_summary, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
