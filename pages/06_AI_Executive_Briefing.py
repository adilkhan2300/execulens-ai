"""
ExecuLens AI - Page 6: AI Executive Briefing
Synthesizes computed analytics into an 8-section evidence-backed executive briefing
using OpenAI API (or deterministic zero-API fallback).
"""

import streamlit as st
import json
from config.settings import format_currency, format_percentage, OPENAI_API_KEY, OPENAI_MODEL
from src.data_ingestion import get_data_store
from src.kpi_engine import compute_executive_scorecard
from src.financial_analysis import decompose_profit_variance
from src.driver_analysis import build_aligned_analysis_matrix, analyze_kpi_correlations
from src.root_cause import investigate_performance_event
from src.recommendation_engine import generate_automated_recommendations
from src.llm_service import generate_executive_briefing
from src.reporting import generate_pdf_executive_report
from src.ui_components import apply_executive_styles, render_page_header

def render():
    apply_executive_styles()
    store = get_data_store()
    fin_df = store.financial_df
    ops_df = store.operational_df
    events_df = store.events_df
    defs_dict = store.kpi_defs_df.set_index("kpi_name").to_dict(orient="index") if store.kpi_defs_df is not None else {}

    render_page_header(
        title="AI Executive Briefing",
        subtitle="LLM-synthesized 8-part strategic briefing backed strictly by verified Python calculations.",
        badge="Page 06"
    )

    if fin_df is None or fin_df.empty:
        st.warning("Financial datasets unavailable.")
        return

    # Engine status banner
    if OPENAI_API_KEY:
        st.success(f"🟢 **LLM Active:** Connected to OpenAI ({OPENAI_MODEL}). Safeguards enforce strict numeric citation.")
    else:
        st.info("🔵 **Zero-API Mode Active:** Using Deterministic Rule-Based Intelligence Engine. No external network credentials required.")

    # Build Structured Evidence Package
    scorecard = compute_executive_scorecard(fin_df)
    sorted_dates = sorted(fin_df["date"].unique())
    p1 = sorted_dates[-2] if len(sorted_dates) > 1 else sorted_dates[0]
    p2 = sorted_dates[-1]

    matrix_df, kpi_cols, _ = build_aligned_analysis_matrix(fin_df, ops_df)
    drivers = analyze_kpi_correlations(matrix_df, "operating_profit", kpi_cols, defs_dict)
    rc = investigate_performance_event(fin_df, ops_df, events_df, defs_dict, p1, p2)
    recs = generate_automated_recommendations(rc.get("adverse_kpis", []), scorecard)

    evidence_package = {
        "scorecard": scorecard,
        "current_period": p2,
        "previous_period": p1,
        "financial_decomposition": rc.get("financial_decomposition", {}),
        "adverse_kpis": rc.get("adverse_kpis", []),
        "top_drivers": drivers.to_dict(orient="records")[:5],
        "root_cause": rc,
        "recommendations": recs[:5],
    }

    # Session caching for briefing
    if "briefing_content" not in st.session_state or st.button("🔄 Regenerate Executive Briefing"):
        with st.spinner("Compiling evidence package and generating executive briefing..."):
            briefing_text, mode_used = generate_executive_briefing(evidence_package)
            st.session_state["briefing_content"] = briefing_text
            st.session_state["briefing_mode"] = mode_used

    briefing_text = st.session_state.get("briefing_content", "")
    mode_used = st.session_state.get("briefing_mode", "Deterministic Engine")

    st.caption(f"Generated via: **{mode_used}** | Reporting Horizon: **{p1} to {p2}**")

    # Display briefing markdown inside container
    st.markdown("---")
    st.markdown(briefing_text)
    st.markdown("---")

    # PDF Download Action
    col_dl, col_view = st.columns([1, 1])
    with col_dl:
        pdf_bytes = generate_pdf_executive_report(
            scorecard,
            drivers.to_dict(orient="records"),
            rc.get("hypotheses", []),
            recs,
            briefing_text=briefing_text
        )
        st.download_button(
            label="📥 Download Executive Briefing as PDF",
            data=pdf_bytes,
            file_name=f"ExecuLens_AI_Briefing_{p2}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with col_view:
        with st.expander("🔍 View Raw Structured Evidence Package (JSON)"):
            st.json(evidence_package)

if __name__ == "__main__":
    render()
