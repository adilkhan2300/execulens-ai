"""
ExecuLens AI - Page 5: Financial Impact Analysis
Translates operational deviations into defensible, business-relevant financial estimates
with documented formulas, explicit assumptions, and low/base/high scenario uncertainty bounds.
"""

import streamlit as st
import pandas as pd
from config.settings import format_currency, format_percentage
from src.data_ingestion import get_data_store
from src.financial_analysis import analyze_budget_variances
from src.financial_impact import (
    model_conversion_rate_impact,
    model_cac_impact,
    model_stockout_impact,
    model_turnover_cost_impact,
    model_fulfillment_cost_impact
)
from src.ui_components import apply_executive_styles, render_page_header

def render():
    apply_executive_styles()
    store = get_data_store()
    fin_df = store.financial_df
    ops_df = store.operational_df

    render_page_header(
        title="Financial Impact Modeling Center",
        subtitle="Translate operational KPI movements into quantified P&L impact estimates with low/base/high bounds.",
        badge="Page 05"
    )

    if fin_df is None or fin_df.empty:
        st.warning("Financial datasets unavailable.")
        return

    tab_models, tab_budget = st.tabs([
        "💰 Operational Impact Models (Low / Base / High)",
        "📊 Actual vs Budget Variance Decompositions"
    ])

    with tab_models:
        st.markdown("#### **Interactive Financial Variance Translators**")
        st.caption("All estimates use explicit business assumptions and state clear scenario uncertainty bounds.")

        c_sel = st.selectbox(
            "Select Operational Impact Model",
            [
                "1. Sales Conversion Rate Impact on Revenue",
                "2. Customer Acquisition Cost (CAC) Expense Impact",
                "3. Stockout Rate & Inventory Availability Revenue Loss",
                "4. Employee Turnover & Recruitment Replacement Costs",
                "5. Order Fulfillment Unit Cost Margin Variance"
            ]
        )

        st.markdown("---")

        if "1. Sales Conversion" in c_sel:
            st.markdown("##### **Model: Sales Conversion Rate Impact**")
            col1, col2, col3 = st.columns(3)
            with col1:
                cur_rate = st.slider("Current Conversion Rate (%)", 1.0, 8.0, 4.1, 0.1)
            with col2:
                tgt_rate = st.slider("Target Conversion Rate (%)", 1.0, 8.0, 4.5, 0.1)
            with col3:
                aov = st.number_input("Average Order Value ($)", value=3800.0, step=100.0)

            orders_vol = st.number_input("Base Monthly Order Volume", value=1200, step=50)

            impact = model_conversion_rate_impact(orders_vol, aov, cur_rate, tgt_rate)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Low Scenario", format_currency(impact["low_scenario"]))
            m2.metric("Base Financial Impact", format_currency(impact["base_financial_impact"]))
            m3.metric("High Scenario", format_currency(impact["high_scenario"]))
            
            st.info(f"**Mathematical Formula:** `{impact['formula']}`\n\n**Assumptions:** {impact['assumptions']}")

        elif "2. Customer Acquisition Cost" in c_sel:
            st.markdown("##### **Model: Customer Acquisition Cost (CAC) Variance**")
            col1, col2 = st.columns(2)
            with col1:
                cur_cac = st.number_input("Current CAC ($)", value=1420.0, step=25.0)
                tgt_cac = st.number_input("Target CAC ($)", value=1250.0, step=25.0)
            with col2:
                customers = st.number_input("New Customers Acquired in Cohort", value=850, step=25)

            impact = model_cac_impact(customers, cur_cac, tgt_cac)
            m1, m2, m3 = st.columns(3)
            m1.metric("Conservative Bound", format_currency(impact["low_scenario"]))
            m2.metric("Base Profit Impact", format_currency(impact["base_financial_impact"]))
            m3.metric("Optimistic Bound", format_currency(impact["high_scenario"]))
            st.info(f"**Formula:** `{impact['formula']}`\n\n**Assumptions:** {impact['assumptions']}")

        elif "3. Stockout Rate" in c_sel:
            st.markdown("##### **Model: Inventory Stockouts & Lost Revenue**")
            col1, col2 = st.columns(2)
            with col1:
                stk_rate = st.slider("Observed Stockout Rate (%)", 0.5, 12.0, 3.8, 0.1)
                tgt_stk = st.slider("Target Buffer Stockout (%)", 0.5, 5.0, 1.8, 0.1)
            with col2:
                demand = st.number_input("Total Order Demand Volume", value=3200, step=100)
                aov_stk = st.number_input("Average Order Size ($)", value=2100.0, step=100.0)

            impact = model_stockout_impact(demand, aov_stk, stk_rate, tgt_stk)
            m1, m2, m3 = st.columns(3)
            m1.metric("Low Estimate", format_currency(impact["low_scenario"]))
            m2.metric("Base Lost Revenue", format_currency(impact["base_financial_impact"]))
            m3.metric("High Estimate", format_currency(impact["high_scenario"]))
            st.info(f"**Formula:** `{impact['formula']}`\n\n**Assumptions:** {impact['assumptions']}")

        elif "4. Employee Turnover" in c_sel:
            st.markdown("##### **Model: Employee Turnover & Replacement Costs**")
            col1, col2 = st.columns(2)
            with col1:
                cur_turn = st.slider("Current Voluntary Turnover (%)", 4.0, 25.0, 14.2, 0.1)
                tgt_turn = st.slider("Target Benchmark Turnover (%)", 4.0, 15.0, 8.5, 0.1)
            with col2:
                hc = st.number_input("Total Headcount (FTEs)", value=650, step=10)
                sal = st.number_input("Average Annual Salary ($)", value=88000.0, step=2000.0)

            impact = model_turnover_cost_impact(hc, cur_turn, tgt_turn, sal)
            m1, m2, m3 = st.columns(3)
            m1.metric("Low Scenario", format_currency(impact["low_scenario"]))
            m2.metric("Base Replacement Cost", format_currency(impact["base_financial_impact"]))
            m3.metric("High Scenario", format_currency(impact["high_scenario"]))
            st.info(f"**Formula:** `{impact['formula']}`\n\n**Assumptions:** {impact['assumptions']}")

        elif "5. Order Fulfillment" in c_sel:
            st.markdown("##### **Model: Order Fulfillment Unit Cost Variance**")
            col1, col2 = st.columns(2)
            with col1:
                cur_c = st.number_input("Current Cost per Order ($)", value=16.80, step=0.5)
                tgt_c = st.number_input("Target Cost per Order ($)", value=14.50, step=0.5)
            with col2:
                tot_o = st.number_input("Fulfilled Orders Count", value=14500, step=500)

            impact = model_fulfillment_cost_impact(tot_o, cur_c, tgt_c)
            m1, m2, m3 = st.columns(3)
            m1.metric("Low Bound", format_currency(impact["low_scenario"]))
            m2.metric("Base OpEx Impact", format_currency(impact["base_financial_impact"]))
            m3.metric("High Bound", format_currency(impact["high_scenario"]))
            st.info(f"**Formula:** `{impact['formula']}`\n\n**Assumptions:** {impact['assumptions']}")

    with tab_budget:
        st.markdown("#### **Actual vs Budget Variance Performance Matrix**")
        b_df = analyze_budget_variances(fin_df)
        st.dataframe(
            b_df.style.format({
                "actual_revenue": "${:,.0f}",
                "budget_revenue": "${:,.0f}",
                "actual_profit": "${:,.0f}",
                "budget_profit": "${:,.0f}",
                "rev_variance": "${:,.0f}",
                "rev_variance_pct": "{:+.1f}%",
                "profit_variance": "${:,.0f}",
                "profit_variance_pct": "{:+.1f}%"
            }),
            use_container_width=True,
            hide_index=True
        )

if __name__ == "__main__":
    render()
