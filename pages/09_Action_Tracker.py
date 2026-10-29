"""
ExecuLens AI - Page 9: Management Action Tracker
Prioritized management action register, ownership assignment, deadline tracking,
and post-intervention performance review.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from src.database import get_all_actions, upsert_action, delete_action
from src.recommendation_engine import compute_action_priority_score
from src.ui_components import apply_executive_styles, render_page_header

def render():
    apply_executive_styles()

    render_page_header(
        title="Executive Action Tracker & Workflow Register",
        subtitle="Translate diagnostic insights into assigned, prioritized, and auditable management actions.",
        badge="Page 09"
    )

    actions = get_all_actions()

    tab_list, tab_create = st.tabs(["📋 Strategic Action Register", "➕ Log New Strategic Action"])

    with tab_list:
        if not actions:
            st.info("No active management actions in database. Log a new action or generate recommendations.")
        else:
            df_act = pd.DataFrame(actions)
            
            # Display filters
            c_st, c_pr = st.columns(2)
            with c_st:
                status_filter = st.selectbox("Filter Status", ["All", "Proposed", "In Progress", "Completed"], index=0)
            with c_pr:
                priority_filter = st.selectbox("Filter Priority", ["All", "Critical", "High", "Medium", "Low"], index=0)

            filtered_act = df_act.copy()
            if status_filter != "All":
                filtered_act = filtered_act[filtered_act["status"] == status_filter]
            if priority_filter != "All":
                filtered_act = filtered_act[filtered_act["priority"] == priority_filter]

            st.dataframe(
                filtered_act[[
                    "action_id", "date_created", "related_kpi", "action_description",
                    "owner", "priority", "status", "expected_impact", "actual_impact", "review_date"
                ]],
                use_container_width=True,
                hide_index=True
            )

            st.markdown("---")
            st.markdown("##### **Update Existing Action Status**")
            col_sel, col_new_st, col_btn = st.columns([2, 1, 1])
            with col_sel:
                action_to_update = st.selectbox("Select Action ID", df_act["action_id"].tolist())
            with col_new_st:
                new_status = st.selectbox("New Status", ["Proposed", "Approved", "In Progress", "Completed"])
            with col_btn:
                st.write("")
                st.write("")
                if st.button("Update Status"):
                    act_record = next(a for a in actions if a["action_id"] == action_to_update)
                    act_record["status"] = new_status
                    upsert_action(act_record)
                    st.success(f"Action {action_to_update} updated to {new_status}!")
                    st.rerun()

            # CSV Download
            csv_data = df_act.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Actions to CSV",
                data=csv_data,
                file_name="ExecuLens_Action_Register.csv",
                mime="text/csv"
            )

    with tab_create:
        st.markdown("#### **Register New Executive Management Action**")
        with st.form("new_action_form"):
            f_kpi = st.text_input("Related KPI", value="Sales Conversion Rate")
            f_out = st.text_input("Related Financial Outcome", value="Operating Profit")
            f_desc = st.text_area("Strategic Action Description", value="Implement refreshed consultative sales methodology and CRM qualification gating.")
            
            c_o, c_p, c_u = st.columns(3)
            with c_o:
                f_owner = st.text_input("Action Owner / Executive Role", value="VP Commercial Sales")
            with c_p:
                f_priority = st.selectbox("Priority Level", ["Critical", "High", "Medium", "Low"], index=1)
            with c_u:
                f_urgency = st.selectbox("Urgency", ["High", "Medium", "Low"], index=0)

            c_exp, c_rev = st.columns(2)
            with c_exp:
                f_exp = st.text_input("Expected Business Impact", value="+0.4% conversion uplift within 60 days")
            with c_rev:
                f_rev = st.date_input("Target Review Date")

            submitted = st.form_submit_button("Submit & Persist Action")
            if submitted:
                new_id = f"ACT-{datetime.now().strftime('%Y%m%d-%H%M')}"
                new_rec = {
                    "action_id": new_id,
                    "date_created": datetime.now().strftime("%Y-%m-%d"),
                    "related_kpi": f_kpi,
                    "related_financial_outcome": f_out,
                    "action_description": f_desc,
                    "owner": f_owner,
                    "priority": f_priority,
                    "status": "Proposed",
                    "expected_impact": f_exp,
                    "actual_impact": "Pending initial review",
                    "review_date": str(f_rev)
                }
                upsert_action(new_rec)
                st.success(f"New action {new_id} recorded successfully in SQLite register!")
                st.rerun()

if __name__ == "__main__":
    render()
