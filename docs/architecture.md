# AcreOps architecture

AcreOps is a multi-agent platform for real-estate development and property operations. Each agent is a LangGraph `StateGraph` with typed state, a checkpointer, and an audit list. FastAPI exposes the graphs. Streamlit is the operator console. Adapters isolate third-party systems so demo mode never needs secrets.

## Principles

1. **Code decides, models narrate.** Vendor selection, permit diffs, LightGBM inference, and BIM occupancy math are deterministic. An LLM, if configured, only writes the executive summary or SMS copy.
2. **Irreversible writes have a human gate.** The drone graph uses LangGraph `interrupt()` so a superintendent must approve before `schedule_updated` can flip. Feasibility PDFs are stamped as decision-support, not a PE / appraisal.
3. **Same path in demo and prod.** `send_sms`, `create_and_send_packet`, `upsert_timeline_event`, and `scrape_portal` always return the same shape. Live credentials change the side effect, not the contract.
4. **Catalogs are fixtures, not mocks inside the agent.** Agents read `data/*.json` through `acreops.adapters.catalog`. Tests hit the real graphs.

## Agent graphs

### Site feasibility kit

`START → zoning → comps → demographics → underwrite → packet → END`

- Zoning / comps / demographics compile from the parcel catalog (stand-in for municipal GIS + MLS + ACS).
- Underwrite builds three capacity scenarios (by-right, density bonus, conservative) and a residual land value.
- Packet renders a ReportLab PDF and opens a PandaDoc document (create-from-PDF + recipients). Status stays `document.draft` until a human sends.

### Tenant ticket triage

`START → classify → assign → notify → END`

- Classifier is a rule engine with emergency / urgent / routine / tenant-responsibility tiers and trade routing. That is deliberate: Fair Housing and life-safety routing should not drift with a prompt.
- Vendor pick is constrained search on the Airtable-shaped bench (trade + zone + emergency flag + rating + response time).
- Notify writes the work order and sends tenant + vendor SMS via the comms adapter.
- Inbound path is `POST /webhooks/appfolio` so an AppFolio `work_order.created` webhook can land on the same graph.

### Permit pulse

`START → poll → diff → notify → END`

- `scrape_portal` is the Selenium stand-in. In live mode it would drive Accela / EnerGov / custom city search forms and hash the status element.
- Diff compares against an in-process last-seen map. Actionable statuses (corrections, approved, failed inspection, denied, expired) mark `action_required`.
- Notify emails the PM and upserts a Notion timeline row per change.

### Drone progress checker

`START → analyze → validate → report → END`

- Analyze overlays demo observations (orthomosaic occupancy) on the 4D BIM element list, computes per-element `%` and a rough schedule delta.
- Flags: behind schedule, ahead, occlusion, geometry mismatch. Occluded elements must not move dates.
- Validate calls `interrupt()` unless `skip_interrupt=True` (API demo). Resume with `POST /agents/drone/validate`.
- Report writes the PDF only after the gate. `schedule_updated` stays false unless the superintendent explicitly opts in.

### Lease-churn predictor

`START → score → offers → END`

- Features: days-to-expiry, tenure, prior renewals, late ratio, NSF, open / unresolved WOs, maintenance days, portal logins, CSAT, autopay, neighborhood vacancy, building move-outs, rent-to-market, offered increase.
- Model: LightGBM binary, trained on a synthetic frame whose latent logit matches those drivers. `load_or_train()` persists `artifacts/churn_lightgbm.txt`.
- Offers are driver-matched (maintenance credit vs. increase cap vs. payment plan vs. market match). Emails go out through the comms adapter.

## Trust surface

| Risk | Control |
|---|---|
| Hallucinated zoning standard | Catalog + citations on the PDF; no free-form ordinance generation in demo |
| Wrong vendor at 2am | Deterministic eligibility filters before any model tie-break |
| Schedule slip from a bad drone read | Superintendent interrupt; occlusions cannot update dates |
| Discriminatory renewal offers | Incentive is computed from operational drivers, not protected-class fields |
| Silent portal miss | Pulse always emits snapshots; empty `changes` is a successful no-op |

## What is intentionally not in v0.1

- Live municipal GIS / Regrid / FEMA calls (parcel catalog is the seam).
- Real UAV photogrammetry / IFC parsing (observation JSON is the seam).
- Multi-tenant auth and row-level property ACLs.
- MLflow registry for the churn model (ProcureLens-style promotion can land next).
