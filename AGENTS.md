# AcreOps agent notes

This repo is a multi-agent real-estate / construction platform. Keep these rules when extending it.

## Non-negotiables

- Vendor assignment, permit diffs, LightGBM inference, and BIM occupancy math stay in code. Do not move them behind a prompt.
- The drone graph must keep the superintendent `interrupt()` before `schedule_updated` can become true.
- Feasibility PDFs are decision-support. Never imply a PE stamp, survey, or appraisal.
- Incentive offers must be derived from operational drivers (maintenance, price, payment, market). Do not add protected-class features.
- Demo mode must keep working with no API keys. Adapters return the same shape live or stubbed.

## How to add an agent

1. Pydantic contracts in `src/acreops/schemas/`.
2. LangGraph `StateGraph` with `AuditTrail` reducer on `audit`.
3. Catalog or adapter seam in `src/acreops/adapters/`.
4. FastAPI route on `/agents/<name>`.
5. Streamlit tab in `ui/app.py`.
6. Pytest + an eval case in `evals/run_evals.py`.

## Commands

```bash
make api
make ui
make test
make evals
acreops feasibility --address "1408 East 6th Street" --city Austin --state TX
```
