"""
ExecuLens AI - Page 4: Root-Cause Investigation Engine
Interactive diagnostic drill-down for major performance changes:
variance decomposition, operational shifts, business events, and ranked hypotheses.
"""

import streamlit as st
import pandas as pd
from config.settings import format_currency, format_percentage
from src.data_ingestion import get_data_store
from src.root_cause import investigate_performance_event
from src.ui_components import (
    apply_executive_styles,
    render_page_header,
    create_waterfall_chart
)

def render():
    apply_executive_styles()
    store = get_data_store()
    fin_df = store.financial_df
    ops_df = store.operational_df
    events_df = store.events_df
    defs_dict = store.kpi_defs_df.set_index("kpi_name").to_dict(orient="index") if store.kpi_defs_df is not None else {}

    render_page_header(
        title="Root-Cause Diagnostic Engine",
        subtitle="Investigate why financial and operational performance changed between two comparison horizons.",
        badge="Page 04"
    )

    if fin_df is None or fin_df.empty:
        st.warning("Financial datasets unavailable.")
        return

    dates = sorted(fin_df["date"].unique())
    if len(dates) < 2:
        st.error("At least two distinct monthly periods are required for comparative investigation.")
        return

    # Period Selection Bar
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        start_p = st.selectbox("Baseline Period (T1)", dates, index=len(dates)-2)
    with c_p2:
        end_p = st.selectbox("Comparison Period (T2)", dates, index=len(dates)-1)

    if start_p >= end_p:
        st.warning("⚠️ Comparison Period (T2) should ideally be chronologically after Baseline Period (T1).")

    # Run Investigation
    with st.spinner("Executing 10-step root-cause diagnostics..."):
        investigation = investigate_performance_event(
            fin_df, ops_df, events_df, defs_dict, start_p, end_p
        )

    if not investigation.get("success"):
        st.error(investigation.get("error"))
        return

    fin_decomp = investigation["financial_decomposition"]
    tot_change = investigation["total_profit_change"]
    pct_change = investigation["pct_profit_change"]

    # Top Level Variance Summary
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Baseline Profit", format_currency(fin_decomp.get("base_profit", 0)))
    s2.metric("Comparison Profit", format_currency(fin_decomp.get("final_profit", 0)))
    s3.metric("Total Profit Change", format_currency(tot_change), f"{pct_change:+.1f}%")
    s4.metric("Primary Declining BU", investigation.get("primary_declining_bu", "N/A"))

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Waterfall Chart
    fig_waterfall = create_waterfall_chart(fin_decomp.get("waterfall_items", []))
    st.plotly_chart(fig_waterfall, use_container_width=True)

    # Diagnostic Tabs
    tab_hypo, tab_kpis, tab_events, tab_bu = st.tabs([
        "🔬 Ranked Diagnostic Hypotheses",
        "📉 Operational KPI Shifts",
        "🗓️ Concurrent Business Events",
        "🏢 Business Unit Variance Breakdown"
    ])

    with tab_hypo:
        st.markdown("#### **Evidence-Backed Diagnostic Explanations**")
        hypotheses = investigation.get("hypotheses", [])
        
        for h in hypotheses:
            conf_badge = "🟢 High" if h["evidence_strength"] == "High" else ("🟡 Moderate" if h["evidence_strength"] in ["Medium", "Moderate"] else "⚪ Low")
            with st.expander(f"**Hypothesis #{h['rank']}: {h['hypothesis']}** — *Confidence: {conf_badge}*", expanded=True):
                st.markdown("**Supporting Evidence:**")
                for ev in h["supporting_evidence"]:
                    st.markdown(f"- {ev}")
                
                st.markdown(f"**Contradicting / Moderating Evidence:**\n- {h['contradicting_evidence']}")
                st.markdown(f"**Estimated Financial Relevance:** {h['magnitude']}")
                st.info(f"📋 **Recommended Management Validation Step:** {h['suggested_validation']}")

    with tab_kpis:
        st.markdown("#### **Operational Indicators Exhibiting Adverse Swings**")
        adverse = investigation.get("adverse_kpis", [])
        if adverse:
            df_adv = pd.DataFrame(adverse)
            st.dataframe(
                df_adv[["department", "kpi_name", "period_1_val", "period_2_val", "pct_delta", "direction"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("No operational KPIs recorded adverse movements beyond normal tolerance.")

    with tab_events:
        st.markdown("#### **Documented Corporate Events During Investigation Window**")
        events = investigation.get("business_events", [])
        if events:
            st.dataframe(pd.DataFrame(events), use_container_width=True, hide_index=True)
        else:
            st.info("No formal corporate business events were cataloged during this exact window.")

    with tab_bu:
        st.markdown("#### **Profit Variance Contribution by Business Unit**")
        bu_c = fin_decomp.get("bu_contributions", {})
        df_bu_c = pd.DataFrame(list(bu_c.items()), columns=["Business Unit", "Operating Profit Change ($)"])
        df_bu_c["Profit Change ($) Formatted"] = df_bu_c["Operating Profit Change ($)"].apply(format_currency)
        st.dataframe(df_bu_c, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    render()
