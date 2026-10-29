"""
ExecuLens AI - Page 8: Scenario Simulator & Performance Forecasting
Time-series trajectory forecasting, interactive what-if levers, sensitivity grids,
and 5-way strategic scenario comparison.
"""

import streamlit as st
import pandas as pd
from config.settings import format_currency, format_percentage
from src.data_ingestion import get_data_store
from src.forecasting import generate_financial_forecast
from src.scenario_engine import (
    get_baseline_operating_state,
    simulate_what_if_scenario,
    generate_scenario_matrix_comparison,
    compute_2d_sensitivity_grid
)
from src.ui_components import (
    apply_executive_styles,
    render_page_header,
    create_forecast_chart,
    create_scenario_comparison_chart
)

def render():
    apply_executive_styles()
    store = get_data_store()
    fin_df = store.financial_df

    render_page_header(
        title="Performance Forecasting & Scenario Simulator",
        subtitle="Simulate potential strategic management interventions, evaluate sensitivity, and forecast financial trajectories.",
        badge="Page 08"
    )

    if fin_df is None or fin_df.empty:
        st.warning("Financial datasets unavailable.")
        return

    baseline = get_baseline_operating_state(fin_df)

    tab_forecast, tab_whatif, tab_matrix, tab_sensitivity = st.tabs([
        "📈 Trajectory Forecasting",
        "🎛️ Interactive What-If Simulator",
        "⚖️ Strategic Scenario Comparison",
        "🔬 2D Sensitivity Analysis"
    ])

    with tab_forecast:
        st.markdown("#### **Performance Horizon Forecasting (Chronological Holdout Validation)**")
        c_m, c_h = st.columns(2)
        with c_m:
            target_metric = st.selectbox("Forecast Target Metric", ["revenue", "operating_profit", "cost_of_goods_sold", "operating_expenses"], index=0)
        with c_h:
            horizon = st.slider("Forecast Horizon (Months Ahead)", 3, 12, 6)

        fc_result = generate_financial_forecast(fin_df, target_metric=target_metric, forecast_horizon=horizon)
        if fc_result.get("success"):
            fig_fc = create_forecast_chart(fc_result)
            st.plotly_chart(fig_fc, use_container_width=True)

            metrics = fc_result.get("evaluation_metrics", {})
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Holdout Out-of-Sample MAE", f"${metrics.get('mae', 0):,.0f}")
            m2.metric("RMSE", f"${metrics.get('rmse', 0):,.0f}")
            m3.metric("MAPE", f"{metrics.get('mape_pct', 0):.1f}%")
            m4.metric("Validation Split", f"{metrics.get('train_months')} train / {metrics.get('test_months')} test")
            st.caption(f"**Model Type:** {fc_result.get('model_name')}. {fc_result.get('limitations')}")
        else:
            st.error(fc_result.get("error"))

    with tab_whatif:
        st.markdown("#### **Executive Strategic Levers**")
        st.caption(f"Adjust levers relative to current monthly baseline (Revenue: {format_currency(baseline.get('revenue', 0))}, Operating Profit: {format_currency(baseline.get('operating_profit', 0))}).")

        col_l1, col_l2, col_l3 = st.columns(3)
        with col_l1:
            conv_delta = st.slider("Sales Conversion Rate Uplift (%)", -20.0, 25.0, 5.0, 1.0)
            aov_delta = st.slider("Average Order Value Change (%)", -15.0, 20.0, 0.0, 1.0)
        with col_l2:
            cac_delta = st.slider("CAC Budget Shift (%)", -25.0, 25.0, -10.0, 1.0)
            stockout_red = st.slider("Stockout Rate Reduction (%)", 0.0, 50.0, 20.0, 5.0)
        with col_l3:
            fulf_delta = st.slider("Fulfillment Cost per Order Change (%)", -25.0, 25.0, -5.0, 1.0)
            turn_red = st.slider("Employee Turnover Reduction (%)", 0.0, 40.0, 15.0, 5.0)

        sim_res = simulate_what_if_scenario(
            baseline,
            conversion_rate_delta_pct=conv_delta,
            aov_delta_pct=aov_delta,
            cac_delta_pct=cac_delta,
            fulfillment_cost_delta_pct=fulf_delta,
            turnover_reduction_pct=turn_red,
            stockout_reduction_pct=stockout_red,
            scenario_name="Executive Simulated Plan"
        )

        st.markdown("---")
        st.markdown("##### **Projected Simulation Results:**")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Projected Revenue", format_currency(sim_res["simulated_revenue"]), f"{sim_res['revenue_delta_pct']:+.1f}%")
        r2.metric("Projected Operating Profit", format_currency(sim_res["simulated_operating_profit"]), f"{sim_res['profit_delta_pct']:+.1f}%")
        r3.metric("Operating Margin", f"{sim_res['simulated_margin_pct']:.1f}%", f"{sim_res['margin_delta_pts']:+.1f} pts")
        r4.metric("Net Profit Delta", format_currency(sim_res["profit_delta"]))

    with tab_matrix:
        st.markdown("#### **Standardized 5-Way Scenario Comparison**")
        scen_df = generate_scenario_matrix_comparison(baseline)
        fig_scen = create_scenario_comparison_chart(scen_df)
        st.plotly_chart(fig_scen, use_container_width=True)
        st.dataframe(
            scen_df.style.format({
                "Revenue": "${:,.0f}",
                "Revenue Delta": "${:,.0f}",
                "Operating Profit": "${:,.0f}",
                "Profit Delta": "${:,.0f}",
                "Profit Growth (%)": "{:+.1f}%",
                "Operating Margin (%)": "{:.1f}%"
            }),
            use_container_width=True,
            hide_index=True
        )

    with tab_sensitivity:
        st.markdown("#### **2D Sensitivity Matrix: Operating Profit ($)**")
        st.caption("Inspect sensitivity of Operating Profit across varying Conversion Rate uplift and CAC budget adjustments.")
        grid_df = compute_2d_sensitivity_grid(baseline, "conversion_rate_delta_pct", "cac_delta_pct")
        st.dataframe(grid_df.style.format("${:,.0f}"), use_container_width=True)

if __name__ == "__main__":
    render()
