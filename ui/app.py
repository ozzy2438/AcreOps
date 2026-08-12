from __future__ import annotations

import os
from datetime import date

import httpx
import streamlit as st

API = os.environ.get("ACREOPS_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="AcreOps", page_icon="▣", layout="wide")

NAVY = "#0F2744"
TEAL = "#1F6F6A"
SAND = "#F4EFE6"

st.markdown(
    f"""
    <style>
      .stApp {{ background: {SAND}; }}
      h1, h2, h3 {{ color: {NAVY} !important; font-family: Georgia, serif; }}
      .acre-kicker {{
        color: {TEAL}; letter-spacing: 0.14em; font-size: 0.78rem;
        text-transform: uppercase; font-weight: 600; margin-bottom: 0.2rem;
      }}
      div[data-testid="stMetric"] {{
        background: white; border: 1px solid #e4dfd4; padding: 0.6rem 0.8rem;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)


def api(path: str, payload: dict | None = None) -> dict | list:
    url = f"{API}{path}"
    if payload is None:
        return httpx.get(url, timeout=30).json()
    return httpx.post(url, json=payload, timeout=60).json()


st.markdown('<div class="acre-kicker">AcreOps · Real Estate &amp; Construction Agents</div>', unsafe_allow_html=True)
st.title("Operator workspace")
st.caption("Five agents that replace the weekly grind: feasibility kits, ticket triage, permit pulse, drone-vs-BIM, lease churn.")

tab_home, tab_feas, tab_triage, tab_permits, tab_drone, tab_churn = st.tabs(
    ["Overview", "Site feasibility", "Tenant triage", "Permit pulse", "Drone progress", "Lease churn"]
)

with tab_home:
    c1, c2, c3, c4, c5 = st.columns(5)
    try:
        parcels = api("/catalog/parcels")
        vendors = api("/catalog/vendors")
        permits = api("/catalog/permits")
        tenants = api("/catalog/tenants")
        health = api("/health")
    except Exception as exc:
        st.error(f"API not reachable at {API}. Start it with `make api`. ({exc})")
        st.stop()
    c1.metric("Parcels in kit", len(parcels))
    c2.metric("Vendors on bench", len(vendors))
    c3.metric("Watched permits", len(permits))
    c4.metric("Leases in window", len(tenants))
    c5.metric("Service", health.get("version", "—"))
    st.markdown(
        """
| Agent | Replaces | Produces |
|---|---|---|
| **Site feasibility kit** | Broker compiling zoning, comps, demographics | Ready-to-sign PDF + PandaDoc packet |
| **Tenant ticket triage** | Manager reading maintenance mail | Classifier → Airtable vendor + SMS |
| **Permit pulse** | PM refreshing the city portal | Email + Notion timeline on status change |
| **Drone progress checker** | Super eyeballing weekly photos | % complete vs BIM, flagged gaps, human gate |
| **Lease-churn predictor** | Staff guessing renewal offers | LightGBM risk + incentive emails |
"""
    )

with tab_feas:
    st.subheader("Compile a site feasibility kit")
    parcel_opts = {f"{p['address']}, {p['city']}": p for p in parcels}
    chosen = st.selectbox("Demo parcel", list(parcel_opts))
    parcel = parcel_opts[chosen]
    col_a, col_b = st.columns(2)
    with col_a:
        intended = st.selectbox("Intended use", ["multifamily", "mixed_use", "office", "retail", "industrial"])
        land_price = st.number_input("Ask / land price (USD)", min_value=0, value=4500000, step=50000)
    with col_b:
        signer_name = st.text_input("Counterparty signer", "Jordan Hale")
        signer_email = st.text_input("Signer email", "jordan.hale@lp.example")
    if st.button("Run feasibility agent", type="primary"):
        with st.spinner("Zoning, comps, demographics, underwriting, PDF, PandaDoc…"):
            run = api(
                "/agents/feasibility",
                {
                    "address": parcel["address"],
                    "city": parcel["city"],
                    "state": parcel["state"],
                    "zip_code": parcel["zip_code"],
                    "parcel_id": parcel["parcel_id"],
                    "intended_use": intended,
                    "land_price_usd": land_price,
                    "signer_name": signer_name,
                    "signer_email": signer_email,
                    "broker_name": "AcreOps Broker Desk",
                    "broker_email": "broker@acreops.local",
                },
            )
        result = run["result"]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Risk", result["risk_tier"])
        m2.metric("Zone", result["zoning"]["zone_code"])
        m3.metric("By-right units", result["scenarios"][0]["units"])
        m4.metric("PandaDoc", result.get("pandadoc_document_id") or "—")
        st.write(result["executive_summary"])
        st.dataframe(result["scenarios"], use_container_width=True)
        st.caption(f"PDF: `{result.get('pdf_path')}`")
        with st.expander("Audit trail"):
            st.json(run["audit"])

with tab_triage:
    st.subheader("AppFolio-shaped ticket → vendor + SMS")
    desc = st.text_area(
        "Resident description",
        "Kitchen sink is leaking under the cabinet and water is pooling on the floor.",
        height=90,
    )
    c1, c2, c3 = st.columns(3)
    tenant = c1.text_input("Tenant", "Alex Rivera")
    unit = c2.text_input("Unit", "4B")
    prop = c3.selectbox("Property", ["harbor-lofts", "oak-ridge", "cedar-court", "midtown-flats"])
    phone = st.text_input("Tenant mobile", "+15125550001")
    if st.button("Triage ticket", type="primary"):
        run = api(
            "/webhooks/appfolio",
            {
                "tenant_name": tenant,
                "tenant_phone": phone,
                "unit_id": unit,
                "property_id": prop,
                "address": f"{unit} @ {prop}",
                "description": desc,
            },
        )
        wo = run["result"]
        clf = wo["classification"]
        m1, m2, m3 = st.columns(3)
        m1.metric("Severity", clf["severity"])
        m2.metric("Trade", clf["trade"])
        m3.metric("SLA (h)", clf["sla_hours"])
        st.write(clf["reasoning"])
        if wo.get("vendor"):
            st.success(f"Assigned {wo['vendor']['name']} · {wo['vendor']['phone']}")
        st.info(wo.get("tenant_sms") or "No tenant SMS drafted.")
        if wo.get("vendor_sms"):
            st.warning(wo["vendor_sms"])

with tab_permits:
    st.subheader("Nightly portal pulse")
    st.dataframe(permits, use_container_width=True)
    force = st.checkbox("Simulate a status change on this pass", value=True)
    if st.button("Run permit pulse", type="primary"):
        run = api("/agents/permits", {"force_change": force})
        changes = run["result"]["changes"]
        if not changes:
            st.info("No status changes this pass.")
        else:
            st.dataframe(changes, use_container_width=True)
            st.caption("Emails queued to the PM and Notion timeline rows upserted (demo adapters).")
        with st.expander("Snapshots"):
            st.json(run["result"]["snapshots"])

with tab_drone:
    st.subheader("Vision estimate vs. 4D BIM")
    if st.button("Run drone progress checker", type="primary"):
        run = api(
            "/agents/drone",
            {
                "project_name": "East 6th Lofts",
                "flight_date": date.today().isoformat(),
                "skip_interrupt": True,
            },
        )
        result = run["result"]
        m1, m2, m3 = st.columns(3)
        m1.metric("Planned", f"{result['overall_planned_pct']}%")
        m2.metric("Observed", f"{result['overall_observed_pct']}%")
        m3.metric("Schedule Δ", f"{result['schedule_delta_days']:+} d")
        st.write(result["narrative"])
        st.dataframe(result["elements"], use_container_width=True)
        st.markdown("**Flagged discrepancies — superintendent must validate before the look-ahead moves.**")
        st.dataframe(result["discrepancies"], use_container_width=True)
        st.caption(f"PDF: `{result.get('pdf_path')}` · schedule updated: {result.get('schedule_updated')}")

with tab_churn:
    st.subheader("LightGBM renewal risk + incentive emails")
    horizon = st.slider("Horizon (days)", 30, 180, 90)
    floor = st.slider("Min churn probability", 0.1, 0.8, 0.35)
    if st.button("Score portfolio & draft offers", type="primary"):
        run = api(
            "/agents/churn",
            {"horizon_days": horizon, "min_probability": floor, "send_email": True},
        )
        preds = run["result"]["predictions"]
        offers = run["result"]["offers"]
        if not preds:
            st.info("No tenants above the risk floor in this window.")
        else:
            st.dataframe(preds, use_container_width=True)
            st.markdown("**Drafted incentive emails**")
            for offer in offers:
                with st.expander(offer["subject"]):
                    st.write(offer["body"])
