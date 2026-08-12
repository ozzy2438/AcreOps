from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from acreops.agents.drone.report import render_progress_pdf
from acreops.agents.drone.vision import (
    estimate_progress,
    flag_discrepancies,
    load_bim,
    schedule_delta_days,
)
from acreops.graphutil import AuditTrail
from acreops.schemas.common import AgentName, AgentRun, AuditEvent
from acreops.schemas.drone import DroneReport, ProgressEstimate


class DroneState(TypedDict, total=False):
    project_name: str | None
    flight_date: str
    elements: list[dict[str, Any]]
    discrepancies: list[dict[str, Any]]
    narrative: str
    overall_planned_pct: float
    overall_observed_pct: float
    schedule_delta_days: float
    superintendent_validated: bool
    superintendent_notes: str | None
    schedule_updated: bool
    pdf_path: str | None
    report_id: str
    audit: AuditTrail
    skip_interrupt: bool


def _audit(action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return AuditEvent(agent=AgentName.DRONE, action=action, payload=payload or {}).model_dump(
        mode="json"
    )


def node_analyze(state: DroneState) -> dict[str, Any]:
    project, bim, observations = load_bim(state.get("project_name"))
    estimates = estimate_progress(bim, observations)
    flags = flag_discrepancies(estimates)
    planned = sum(e.planned_pct for e in estimates) / max(len(estimates), 1)
    observed = sum(e.observed_pct for e in estimates) / max(len(estimates), 1)
    delta_days = schedule_delta_days(estimates)
    delayed = [e.name for e in estimates if e.status.value == "delayed"]
    narrative = (
        f"{project}: drone-vs-BIM pass on {state.get('flight_date', date.today().isoformat())}. "
        f"Overall observed {observed:.1f}% vs planned {planned:.1f}% "
        f"({delta_days:+.1f} days). "
        + (f"Delayed: {', '.join(delayed)}. " if delayed else "No delayed elements. ")
        + f"{len(flags)} discrepancy flag(s) need superintendent review before the look-ahead is touched."
    )
    return {
        "project_name": project,
        "elements": [e.model_dump(mode="json") for e in estimates],
        "discrepancies": [d.model_dump(mode="json") for d in flags],
        "overall_planned_pct": round(planned, 1),
        "overall_observed_pct": round(observed, 1),
        "schedule_delta_days": delta_days,
        "narrative": narrative,
        "report_id": f"DR-{abs(hash(project + str(state.get('flight_date')))) % 100000:05d}",
        "audit": [_audit("vision_vs_bim", {"elements": len(estimates), "flags": len(flags)})],
    }


def node_validate(state: DroneState) -> dict[str, Any]:
    if state.get("skip_interrupt"):
        decision = {
            "approved": True,
            "notes": "Auto-approved in API demo mode. Superintendents must still confirm in the field.",
            "update_schedule": False,
        }
    else:
        decision = interrupt(
            {
                "prompt": "Superintendent review required. Approve findings and optionally update the schedule.",
                "report_id": state.get("report_id"),
                "discrepancies": state.get("discrepancies", []),
            }
        )
    approved = bool(decision.get("approved"))
    update = bool(decision.get("update_schedule")) and approved
    return {
        "superintendent_validated": approved,
        "superintendent_notes": decision.get("notes"),
        "schedule_updated": update,
        "audit": [
            _audit(
                "superintendent_gate",
                {"approved": approved, "schedule_updated": update},
            )
        ],
    }


def node_report(state: DroneState) -> dict[str, Any]:
    report = DroneReport(
        report_id=state["report_id"],
        project_name=state["project_name"] or "Project",
        flight_date=date.fromisoformat(state.get("flight_date") or date.today().isoformat()),
        overall_planned_pct=state["overall_planned_pct"],
        overall_observed_pct=state["overall_observed_pct"],
        schedule_delta_days=state["schedule_delta_days"],
        elements=[ProgressEstimate.model_validate(e) for e in state["elements"]],
        discrepancies=state.get("discrepancies", []),
        narrative=state["narrative"],
        superintendent_validated=bool(state.get("superintendent_validated")),
        superintendent_notes=state.get("superintendent_notes"),
        schedule_updated=bool(state.get("schedule_updated")),
    )
    pdf_path = render_progress_pdf(report)
    return {
        "pdf_path": pdf_path,
        "audit": [_audit("render_report", {"pdf": pdf_path})],
    }


def build_graph():
    graph = StateGraph(DroneState)
    graph.add_node("analyze", node_analyze)
    graph.add_node("validate", node_validate)
    graph.add_node("report", node_report)
    graph.add_edge(START, "analyze")
    graph.add_edge("analyze", "validate")
    graph.add_edge("validate", "report")
    graph.add_edge("report", END)
    return graph.compile(checkpointer=InMemorySaver())


_APP = None


def run_drone_progress(
    project_name: str | None = None,
    flight_date: str | None = None,
    *,
    skip_interrupt: bool = True,
    resume: dict[str, Any] | None = None,
    thread_id: str | None = None,
) -> AgentRun:
    global _APP
    if _APP is None:
        _APP = build_graph()
    tid = thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": tid}}
    payload: dict[str, Any] | Command
    if resume is not None:
        payload = Command(resume=resume)
    else:
        payload = {
            "project_name": project_name,
            "flight_date": flight_date or date.today().isoformat(),
            "skip_interrupt": skip_interrupt,
            "audit": [],
        }
    final = _APP.invoke(payload, config)
    report = {
        "report_id": final.get("report_id"),
        "project_name": final.get("project_name"),
        "flight_date": final.get("flight_date"),
        "overall_planned_pct": final.get("overall_planned_pct"),
        "overall_observed_pct": final.get("overall_observed_pct"),
        "schedule_delta_days": final.get("schedule_delta_days"),
        "elements": final.get("elements", []),
        "discrepancies": final.get("discrepancies", []),
        "narrative": final.get("narrative"),
        "superintendent_validated": final.get("superintendent_validated", False),
        "superintendent_notes": final.get("superintendent_notes"),
        "schedule_updated": final.get("schedule_updated", False),
        "pdf_path": final.get("pdf_path"),
    }
    return AgentRun(
        run_id=tid,
        agent=AgentName.DRONE,
        status="completed",
        finished_at=datetime.utcnow(),
        result=report,
        audit=[AuditEvent.model_validate(a) for a in final.get("audit", [])],
        demo=True,
    )
