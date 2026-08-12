# Live integration seams

Every adapter returns the same pydantic-friendly dict in demo and live mode. Flip the env var, keep the agent graph.

## PandaDoc — feasibility packet

`acreops.adapters.pandadoc.create_and_send_packet`

When `PANDADOC_API_KEY` is set, replace the stub with the official client:

1. `DocumentsApi.create_document` from the generated PDF (multipart or public URL).
2. Poll `status_document` until `document.draft`.
3. `send_document` only after a broker clicks send — do not auto-send from the graph.

See [create from file](https://developers.pandadoc.com/docs/create-document-from-file) and the [Python example](https://github.com/PandaDoc/pandadoc-api-python-client/blob/main/examples/create_from_pdf_by_url_and_send.py).

## AppFolio + Airtable + Twilio — triage

- Inbound: `POST /webhooks/appfolio` accepts a `work_order.created`-shaped body.
- Vendor bench: `AIRTABLE_API_KEY` + `AIRTABLE_BASE_ID` + table `Vendors` with columns Name, Phone, Specialty, Zone, Rating, Emergency, AvgResponseMin, Status.
- SMS: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`.

Classifier and vendor eligibility stay in code. Do not let the model pick a vendor id.

## City portals + Notion — permit pulse

`scrape_portal` is the Selenium stand-in. Live implementation should:

- Target the status element, not the full page (timestamps create noise).
- Hash the status text + permit number.
- Back off on portal redesigns; store CSS selectors per jurisdiction in config, not in the graph.

Notion: `NOTION_API_KEY` + `NOTION_TIMELINE_DATABASE_ID`. The upsert payload already has title, status, project, permit_number, notes.

## Vision + BIM — drone

Swap `data/bim_models.json` observations for a real occupancy pass (point-cloud vs IFC buffer). Keep:

- Per-element planned vs observed.
- Occlusion as a first-class status that cannot update the schedule.
- `interrupt()` before `schedule_updated=True`.

## LightGBM — churn

`make train-churn` writes `artifacts/churn_lightgbm.txt`. Replace `_synthetic_training_frame` with a warehouse extract (payments, work orders, rent roll, comps) without adding protected-class columns. Retrain on a schedule; keep the same `FEATURE_COLUMNS` contract or version the model file.
