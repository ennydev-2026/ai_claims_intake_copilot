from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from api_client import api_get, api_post
from ui_chrome import hide_streamlit_top_bar

st.set_page_config(page_title="Operaciones | Claims Intake Copilot", layout="wide")
hide_streamlit_top_bar()
st.title("AI Claims Intake Copilot — Herramientas internas")
st.caption("Demo dashboard for reviewing recent claims, priorities, and pipeline outputs.")

summary = api_get("/api/v1/claims/dashboard/summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total", summary["total_claims"])
col2.metric("Alta", summary["alta"])
col3.metric("Media", summary["media"])
col4.metric("Baja", summary["baja"])

st.divider()
left, right = st.columns([1, 2])

with left:
    st.subheader("Run sample claim")
    samples = api_get("/api/v1/claims/samples")
    sample_names = [item["sample_name"] for item in samples]
    if not sample_names:
        st.warning("No sample datasets available.")
        selected_sample = None
    else:
        selected_sample = st.selectbox("Sample dataset", options=sample_names)
        if st.button("Process sample", type="primary"):
            result = api_post(f"/api/v1/claims/samples/{selected_sample}/run")
            st.success(f'Processed {result["claim_id"]} with priority {result["priority"]["level"]}.')
            st.json(result)

    st.subheader("Submit custom claim JSON")
    if selected_sample:
        default_payload = api_get(f"/api/v1/claims/samples/{selected_sample}")
        json_payload = st.text_area(
            "Claim payload",
            value=json.dumps(default_payload, ensure_ascii=False, indent=2),
            height=300,
        )
        if st.button("Send custom claim"):
            result = api_post("/api/v1/claims/intake", payload=json.loads(json_payload))
            st.success(f'Processed {result["claim_id"]}.')
            st.json(result)
    elif sample_names:
        st.info("Select a sample above to load a default JSON payload.")

with right:
    st.subheader("Recent claims")
    claims = api_get("/api/v1/claims/recent?limit=50")
    if claims:
        df = pd.DataFrame(claims)
        st.dataframe(
            df[["claim_id", "customer_name", "policy_number", "claim_type", "priority_level", "created_at"]],
            use_container_width=True,
            hide_index=True,
        )
        claim_ids = [row["claim_id"] for row in claims]
        selected_claim = st.selectbox("Claim detail", claim_ids)
        if selected_claim:
            detail = api_get(f"/api/v1/claims/{selected_claim}")
            st.json(detail)
    else:
        st.info("No claims processed yet. Run a sample claim to populate the dashboard.")
