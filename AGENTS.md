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
5. Next.js page under `web/src/app/<name>/` plus a card on the desk.
6. Pytest + an eval case in `evals/run_evals.py`.

## Commands

```bash
make api
make ui
make test
make evals
acreops feasibility --address "1408 East 6th Street" --city Austin --state TX
```

## Cursor Cloud specific instructions

Environment is preconfigured by the startup update script; you should not need to install anything by hand.

- Python: a virtualenv lives at `.venv` (system Python is 3.12; project needs >=3.11). Activate with `source .venv/bin/activate`, or call tools directly via `.venv/bin/<tool>`. The `make` targets (`make api`, `make test`, `make lint`, `make evals`) assume the venv is active. The update script refreshes deps with `pip install -e ".[dev]"`.
- Web: Node 22 is preinstalled. `web/` deps are installed with `npm install` (no lockfile is committed). Run the desk with `make ui` (Next.js dev on :3000). `make ui` also runs `npm install` itself.
- Services (see README "Quick start" and the Makefile): FastAPI on `:8000` (`make api`), Next.js field desk on `:3000` (`make ui`). Start long-running services in tmux. The browser only talks to the web app; `web/src/app/api/backend/[...path]/route.ts` is a BFF proxy onto `ACREOPS_API_URL` (default `http://127.0.0.1:8000`), so the API must be up for UI actions to return data.
- Demo mode is the default (`ACREOPS_ENV=demo`); everything works with no API keys. `.env` is created from `.env.example`; live adapters only activate when their env vars are set.
- Known pre-existing failures (NOT environment problems — reproduce on upstream CI/main; do not "fix" as part of setup):
  - `make lint` / `ruff check src tests` fails on ~22 pre-existing `E501` line-length (plus `B905`/`E402`) violations. `ruff` is unpinned (`ruff>=0.4`) and resolves to a newer version (0.16.x) that enforces `E501`; upstream CI on `main` is red for the same reason.
  - `tests/test_permits.py::test_second_pass_without_force_is_quiet` fails deterministically (a logic issue: the no-force second pass reverts each permit vs. the stored `_LAST_SEEN`). The other tests pass with ~88% coverage; `make evals` passes.
- `scripts/demo.sh` is not marked executable in a fresh checkout, so `make demo` errors with "Permission denied". Run it as `bash scripts/demo.sh` instead.
