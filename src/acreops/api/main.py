from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from acreops import __version__
from acreops.adapters.catalog import bim_models, parcels, permits, tenants, vendors
from acreops.agents.churn.graph import run_churn_sweep
from acreops.agents.drone.graph import run_drone_progress
from acreops.agents.feasibility.graph import run_feasibility
from acreops.agents.permits.graph import run_permit_pulse
from acreops.agents.triage.graph import run_triage
from acreops.schemas.feasibility import FeasibilityRequest
from acreops.schemas.triage import TicketIntake

app = FastAPI(
    title="AcreOps",
    description="Real Estate & Construction Agent Platform",
    version=__version__,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class DroneRequest(BaseModel):
    project_name: str | None = "East 6th Lofts"
    flight_date: str | None = None
    skip_interrupt: bool = True


class ChurnRequest(BaseModel):
    horizon_days: int = 90
    min_probability: float = 0.35
    send_email: bool = True


class PermitRequest(BaseModel):
    force_change: bool = True


class SuperintendentDecision(BaseModel):
    thread_id: str
    approved: bool = True
    notes: str = ""
    update_schedule: bool = False


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "acreops", "version": __version__, "mode": "demo"}


@app.get("/catalog/parcels")
def list_parcels() -> list[dict]:
    return parcels()


@app.get("/catalog/vendors")
def list_vendors() -> list[dict]:
    return vendors()


@app.get("/catalog/permits")
def list_permits() -> list[dict]:
    return permits()


@app.get("/catalog/tenants")
def list_tenants() -> list[dict]:
    return tenants()


@app.get("/catalog/bim")
def list_bim() -> list[dict]:
    return bim_models()


@app.post("/agents/feasibility")
def feasibility(req: FeasibilityRequest) -> dict:
    return run_feasibility(req).model_dump(mode="json")


@app.post("/agents/triage")
def triage(req: TicketIntake) -> dict:
    return run_triage(req).model_dump(mode="json")


@app.post("/agents/permits")
def permits_pulse(req: PermitRequest | None = None) -> dict:
    payload = req or PermitRequest()
    return run_permit_pulse(force_change=payload.force_change).model_dump(mode="json")


@app.post("/agents/drone")
def drone(req: DroneRequest | None = None) -> dict:
    payload = req or DroneRequest()
    return run_drone_progress(
        project_name=payload.project_name,
        flight_date=payload.flight_date,
        skip_interrupt=payload.skip_interrupt,
    ).model_dump(mode="json")


@app.post("/agents/drone/validate")
def drone_validate(decision: SuperintendentDecision) -> dict:
    return run_drone_progress(
        resume={
            "approved": decision.approved,
            "notes": decision.notes,
            "update_schedule": decision.update_schedule,
        },
        thread_id=decision.thread_id,
        skip_interrupt=False,
    ).model_dump(mode="json")


@app.post("/agents/churn")
def churn(req: ChurnRequest | None = None) -> dict:
    payload = req or ChurnRequest()
    return run_churn_sweep(
        horizon_days=payload.horizon_days,
        min_probability=payload.min_probability,
        send_email=payload.send_email,
    ).model_dump(mode="json")


class AppFolioWebhook(BaseModel):
    """AppFolio work_order.created shaped payload."""

    tenant_name: str = "Resident"
    tenant_phone: str | None = None
    tenant_email: str | None = None
    unit_id: str
    property_id: str = "harbor-lofts"
    address: str = ""
    description: str
    photos: list[str] = Field(default_factory=list)


@app.post("/webhooks/appfolio")
def appfolio_webhook(payload: AppFolioWebhook) -> dict:
    intake = TicketIntake(
        source="appfolio",
        tenant_name=payload.tenant_name,
        tenant_phone=payload.tenant_phone,
        tenant_email=payload.tenant_email,
        unit_id=payload.unit_id,
        property_id=payload.property_id,
        address=payload.address or payload.property_id,
        description=payload.description,
        photos=payload.photos,
    )
    return run_triage(intake).model_dump(mode="json")
