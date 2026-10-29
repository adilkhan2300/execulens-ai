"""
ExecuLens AI - Page 3: Driver Analysis
KPI-to-Financial Outcome Intelligence: Pearson/Spearman correlation, explainable Driver Score,
lagged operational effects (0-90 days), and multivariable OLS regression.
"""

import streamlit as st
import pandas as pd
from config.settings import FINANCIAL_OUTCOMES, FINANCIAL_OUTCOME_LABELS
from src.data_ingestion import get_data_store
from src.driver_analysis import (
    build_aligned_analysis_matrix,
    analyze_kpi_correlations,
    run_multivariable_regression
)
from src.lag_analysis import compute_lagged_correlations, batch_lag_screening
from src.ui_components import (
    apply_executive_styles,
    render_page_header,
    create_driver_ranking_chart
)

def render():
    apply_executive_styles()
    store = get_data_store()
    fin_df = store.financial_df
    ops_df = store.operational_df
    defs_dict = store.kpi_defs_df.set_index("kpi_name").to_dict(orient="index") if store.kpi_defs_df is not None else {}

    render_page_header(
        title="KPI Driver Analysis & Outcome Intelligence",
        subtitle="Uncover which operational indicators are statistically associated with financial performance.",
        badge="Page 03"
    )

    if fin_df is None or ops_df is None:
        st.warning("Data matrices not ready.")
        return

    # Outcome selector
    c_out, c_grain = st.columns([2, 1])
    with c_out:
        chosen_outcome = st.selectbox(
            "Select Target Financial Outcome",
            FINANCIAL_OUTCOMES,
            index=1,
            format_func=lambda x: FINANCIAL_OUTCOME_LABELS.get(x, x.title())
        )
    with c_grain:
        grain_choice = st.radio("Aggregation Level", ["Regional & BU Grain", "Corporate Monthly Grain"], index=0)
        grain_param = "monthly_bu_region" if grain_choice == "Regional & BU Grain" else "monthly_aggregate"

    # Build analysis matrix
    matrix_df, kpi_cols, _ = build_aligned_analysis_matrix(fin_df, ops_df, grain=grain_param)
    
    if matrix_df.empty or chosen_outcome not in matrix_df.columns:
        st.warning("Insufficient aligned observations for correlation analysis.")
        return

    # Run Driver Correlation Analysis
    drivers_df = analyze_kpi_correlations(matrix_df, chosen_outcome, kpi_cols, defs_dict)

    tab_ranked, tab_regression, tab_lags, tab_disclaimer = st.tabs([
        "🏆 Driver Ranking & Correlations",
        "📐 Multivariable Regression (OLS)",
        "⏳ Lagged Relationships (0-90 Days)",
        "⚖️ Governance & Causality Notice"
    ])

    with tab_ranked:
        c_chart, c_tbl = st.columns([1, 1])
        with c_chart:
            fig_bar = create_driver_ranking_chart(drivers_df, max_n=10)
            st.plotly_chart(fig_bar, use_container_width=True)

        with c_tbl:
            st.markdown("#### **Top Ranked Operational Drivers**")
            st.caption("Driver Score combines correlation magnitude, statistical reliability (1 - p), cross-period stability, target deviation, and business relevance.")
            disp_cols = [
                "kpi_name", "department", "direction_of_association",
                "pearson_r", "spearman_r", "significance", "driver_score"
            ]
            st.dataframe(drivers_df[disp_cols].head(10), use_container_width=True, hide_index=True)

    with tab_regression:
        st.markdown("#### **Multivariable Ordinary Least Squares (OLS) Model**")
        st.write(f"Evaluating combined predictive effect of top operational indicators on **{FINANCIAL_OUTCOME_LABELS.get(chosen_outcome, chosen_outcome)}**.")
        
        # Allow user to pick features for regression
        default_top = drivers_df["kpi_name"].head(4).tolist() if not drivers_df.empty else []
        selected_features = st.multiselect(
            "Select Independent Operational Features",
            options=kpi_cols,
            default=default_top
        )

        if selected_features:
            reg_results = run_multivariable_regression(matrix_df, chosen_outcome, selected_features)
            if reg_results.get("success"):
                r1, r2, r3 = st.columns(3)
                r1.metric("Model R-Squared (R²)", f"{reg_results['r_squared']:.3f}")
                r2.metric("Adjusted R-Squared", f"{reg_results['adj_r_squared']:.3f}")
                r3.metric("F-Statistic", f"{reg_results['f_statistic']:.1f} (p={reg_results['f_pvalue']:.4f})")

                st.markdown("##### **Feature Coefficients & 95% Confidence Intervals**")
                coef_df = pd.DataFrame(reg_results["coefficients"])
                st.dataframe(coef_df, use_container_width=True, hide_index=True)
            else:
                st.error(f"Regression could not be completed: {reg_results.get('error')}")

    with tab_lags:
        st.markdown("#### **Delayed Operational Effects Screening (0 to 3 Months / 0 to 90 Days)**")
        st.write("Identifies operational metrics whose movements anticipate financial results with a delayed lead/lag horizon.")
        
        # Monthly aggregate matrix for lag screening
        m_matrix, m_kpis, _ = build_aligned_analysis_matrix(fin_df, ops_df, grain="monthly_aggregate")
        lag_summary = batch_lag_screening(m_matrix, chosen_outcome, m_kpis, max_lags=3)
        
        st.dataframe(lag_summary.head(10), use_container_width=True, hide_index=True)
        
        # Deep dive into one KPI lag curve
        selected_lag_kpi = st.selectbox("Inspect Specific KPI Lag Profile", m_kpis, index=0)
        single_lag = compute_lagged_correlations(m_matrix, chosen_outcome, selected_lag_kpi, max_lags=3)
        if single_lag.get("success"):
            st.info(f"📌 **Optimal Lag for {selected_lag_kpi}:** Peak association occurs at **{single_lag['optimal_lag_periods']} month(s)** (~{single_lag['optimal_lag_days']} days) with Pearson r = **{single_lag['peak_correlation']:+.2f}**.")
            lag_df = pd.DataFrame(single_lag["lag_series"])
            st.dataframe(lag_df, use_container_width=True, hide_index=True)

    with tab_disclaimer:
        st.warning("""
        **Methodological Governance Disclaimer:**
        - High correlation coefficients and regression weights represent empirical statistical associations, not definitive proof of causality.
        - Operational KPIs fluctuate alongside external market demand, seasonal promotional cycles, and concurrent business initiatives.
        - Driver rankings serve as an analytical prioritization guide to focus management investigation, not autonomous executive decision-making.
        """)

if __name__ == "__main__":
    render()
