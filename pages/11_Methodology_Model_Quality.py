"""
ExecuLens AI - Page 11: Methodology & Model Quality
Statistical foundations, mathematical formulas, model governance limitations, and system audit log trail.
"""

import streamlit as st
import pandas as pd
from src.database import get_audit_logs
from src.ui_components import apply_executive_styles, render_page_header
from config.settings import DRIVER_SCORE_WEIGHTS, ACTION_PRIORITY_WEIGHTS

def render():
    apply_executive_styles()

    render_page_header(
        title="Methodology, Model Quality & Audit Governance",
        subtitle="Transparent documentation of statistical algorithms, analytical formulas, data coverage, and audit trails.",
        badge="Page 11"
    )

    tab_formulas, tab_limits, tab_audit = st.tabs([
        "📐 Analytical Formulas & Weights",
        "⚖️ Model Governance & Limitations",
        "🛡️ Compliance & System Audit Logs"
    ])

    with tab_formulas:
        st.markdown("#### **Core Analytical Formulas**")

        st.markdown("##### **1. Explainable KPI Driver Score (0-100)**")
        st.latex(r"""
        \text{Driver Score} = 100 \times \left( w_1 \cdot |r_{\text{Pearson}}| + w_2 \cdot (1 - p\text{-value}) + w_3 \cdot \text{Stability} + w_4 \cdot \text{Deviation} + w_5 \cdot \text{Relevance} \right)
        """)
        st.write(f"""
        **Active Configuration Weights:**
        - Association Strength ($w_1$): **{DRIVER_SCORE_WEIGHTS['association_strength']*100:.0f}%**
        - Statistical Reliability ($w_2$): **{DRIVER_SCORE_WEIGHTS['statistical_reliability']*100:.0f}%**
        - Period Stability ($w_3$): **{DRIVER_SCORE_WEIGHTS['stability']*100:.0f}%**
        - Target Deviation ($w_4$): **{DRIVER_SCORE_WEIGHTS['target_deviation']*100:.0f}%**
        - Financial Relevance ($w_5$): **{DRIVER_SCORE_WEIGHTS['financial_relevance']*100:.0f}%**
        """)

        st.markdown("##### **2. Profit Variance Waterfall Decomposition**")
        st.latex(r"""
        \Delta \text{Operating Profit} = \Delta \text{Revenue} - \Delta \text{COGS} - \Delta \text{OpEx}
        """)
        st.latex(r"""
        \Delta \text{Revenue} = \text{Volume Effect} + \text{Price/Mix Effect}
        """)

        st.markdown("##### **3. Action Prioritization Score (0-100)**")
        st.latex(r"""
        \text{Priority Score} = 100 \times \left( w_{\text{urg}} \cdot U + w_{\text{imp}} \cdot I + w_{\text{feas}} \cdot F + w_{\text{ev}} \cdot E \right)
        """)
        st.write(f"""
        **Prioritization Weights:**
        - Urgency ($w_{{urg}}$): **{ACTION_PRIORITY_WEIGHTS['urgency']*100:.0f}%**
        - Financial Impact ($w_{{imp}}$): **{ACTION_PRIORITY_WEIGHTS['financial_impact']*100:.0f}%**
        - Implementation Feasibility ($w_{{feas}}$): **{ACTION_PRIORITY_WEIGHTS['feasibility']*100:.0f}%**
        - Evidence Strength ($w_{{ev}}$): **{ACTION_PRIORITY_WEIGHTS['evidence_strength']*100:.0f}%**
        """)

    with tab_limits:
        st.markdown("#### **Model Governance, Assumptions & Limitations**")
        st.info("""
        1. **Association vs. Causation:** Statistical correlation and regression coefficients indicate observed historical co-movement. They do not constitute proof of isolated causal mechanisms.
        2. **Synthetic Data Boundaries:** While the default demonstration dataset mirrors real enterprise operational couplings, it is synthetic and should not be cited as real corporate performance.
        3. **Out-of-Sample Uncertainty:** Time series projections assume structural macroeconomic stability. Black-swan supply disruptions or strategic price revisions will alter trajectory cones.
        4. **Modeled Financial Impacts:** Operational translations (e.g. conversion loss, turnover cost) use industry benchmark heuristics and must be verified against internal departmental audits before capital commitments.
        """)

    with tab_audit:
        st.markdown("#### **Immutable System Audit Trail (SQLite)**")
        st.caption("Logs all dataset ingestions, briefings generated, and management action decisions.")
        
        logs = get_audit_logs(limit=50)
        if logs:
            df_logs = pd.DataFrame(logs)
            st.dataframe(
                df_logs[["id", "timestamp", "action_type", "user_role", "details"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.write("No audit entries recorded yet.")

if __name__ == "__main__":
    render()
