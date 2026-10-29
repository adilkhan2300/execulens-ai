"""
ExecuLens AI - Page 7: Ask ExecuLens (Conversational Executive QA)
Conversational assistant for senior executives backed by deterministic analytics.
"""

import streamlit as st
from src.data_ingestion import get_data_store
from src.executive_qa import answer_executive_question
from src.ui_components import apply_executive_styles, render_page_header

def render():
    apply_executive_styles()
    store = get_data_store()
    fin_df = store.financial_df
    ops_df = store.operational_df
    events_df = store.events_df
    defs_dict = store.kpi_defs_df.set_index("kpi_name").to_dict(orient="index") if store.kpi_defs_df is not None else {}

    render_page_header(
        title="Ask ExecuLens — Executive Decision Assistant",
        subtitle="Ask business performance questions and receive verified, calculation-backed answers without hallucinations.",
        badge="Page 07"
    )

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            {
                "role": "assistant",
                "content": "Hello. I am **ExecuLens AI**, your virtual business performance analyst. Ask me about your revenue drivers, profit deviations, budget variances, or operational risk priorities."
            }
        ]

    st.markdown("#### 💡 **Suggested Executive Questions (Click to Ask):**")
    sample_queries = [
        "Why did operating profit decline this quarter?",
        "Which KPIs are most closely associated with revenue growth?",
        "Which department has the largest unfavorable budget variance?",
        "Is marketing efficiency improving?",
        "Which operational risks should we address first?",
        "What could happen if fulfillment costs increase by 5%?",
        "Which KPIs should the COO review this week?"
    ]

    cols = st.columns(3)
    clicked_query = None
    for idx, sq in enumerate(sample_queries):
        if cols[idx % 3].button(sq, key=f"sq_{idx}", use_container_width=True):
            clicked_query = sq

    st.markdown("---")

    # Display chat history
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Input
    user_input = st.chat_input("Enter your executive question here...") or clicked_query

    if user_input:
        # Append user message
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing operational records and running calculations..."):
                response_data = answer_executive_question(
                    user_input,
                    fin_df,
                    ops_df,
                    defs_dict,
                    events_df
                )
                answer_text = response_data.get("answer", "")
                st.markdown(answer_text)
                st.session_state["chat_history"].append({"role": "assistant", "content": answer_text})

if __name__ == "__main__":
    render()
