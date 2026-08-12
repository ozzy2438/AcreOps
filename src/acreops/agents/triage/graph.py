from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from acreops.adapters.airtable import upsert_work_order
from acreops.adapters.comms import send_sms
from acreops.agents.triage.classifier import classify_ticket
from acreops.agents.triage.dispatch import select_vendor
from acreops.graphutil import AuditTrail
from acreops.schemas.common import AgentName, AgentRun, AuditEvent
from acreops.schemas.triage import TicketClassification, TicketIntake, Vendor, WorkOrder


class TriageState(TypedDict, total=False):
    intake: dict[str, Any]
    classification: dict[str, Any]
    vendor: dict[str, Any] | None
    work_order: dict[str, Any]
    tenant_sms: dict[str, Any] | None
    vendor_sms: dict[str, Any] | None
    audit: AuditTrail


def _audit(action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return AuditEvent(agent=AgentName.TRIAGE, action=action, payload=payload or {}).model_dump(
        mode="json"
    )


def node_classify(state: TriageState) -> dict[str, Any]:
    intake = TicketIntake.model_validate(state["intake"])
    classification = classify_ticket(intake)
    return {
        "classification": classification.model_dump(mode="json"),
        "audit": [_audit("classify", {"severity": classification.severity.value})],
    }


def node_assign(state: TriageState) -> dict[str, Any]:
    intake = TicketIntake.model_validate(state["intake"])
    classification = TicketClassification.model_validate(state["classification"])
    vendor = select_vendor(intake, classification)
    return {
        "vendor": vendor.model_dump(mode="json") if vendor else None,
        "audit": [_audit("assign_vendor", {"vendor": vendor.vendor_id if vendor else None})],
    }


def node_notify(state: TriageState) -> dict[str, Any]:
    intake = TicketIntake.model_validate(state["intake"])
    classification = TicketClassification.model_validate(state["classification"])
    vendor = Vendor.model_validate(state["vendor"]) if state.get("vendor") else None
    wo_id = f"WO-{abs(hash(intake.unit_id + intake.description)) % 100000:05d}"

    tenant_body: str
    vendor_sms = None
    tenant_sms = None
    status = "triaged"
    if classification.tenant_responsibility:
        tenant_body = (
            f"Hi {intake.tenant_name.split()[0]}, we received your note about "
            f"'{intake.description[:80]}'. This looks like a tenant-responsibility item "
            f"(lease §8). Reply HELP if you want a vendor at tenant cost. Ref {wo_id}."
        )
        status = "complete"
    elif vendor:
        tenant_body = (
            f"Got it — {classification.severity.value} {classification.trade.value} ticket {wo_id}. "
            f"{vendor.name} assigned, typical arrival {vendor.avg_response_min} min. "
            f"We'll text when they're en route."
        )
        vendor_sms = send_sms(
            vendor.phone,
            (
                f"AcreOps {classification.severity.value.upper()} {wo_id}: {intake.address} "
                f"unit {intake.unit_id}. {intake.description[:140]}. "
                f"SLA {classification.sla_hours}h. Reply ETA."
            ),
            kind="vendor_dispatch",
        )
        status = "dispatched"
    else:
        tenant_body = (
            f"We have your request {wo_id} and a manager is assigning a vendor. "
            f"We'll update you shortly."
        )
        status = "needs_human"

    if intake.tenant_phone:
        tenant_sms = send_sms(intake.tenant_phone, tenant_body, kind="tenant_update")

    airtable = upsert_work_order(
        {
            "work_order_id": wo_id,
            "unit_id": intake.unit_id,
            "severity": classification.severity.value,
            "trade": classification.trade.value,
            "vendor": vendor.name if vendor else None,
            "status": status,
        }
    )
    work_order = WorkOrder(
        work_order_id=wo_id,
        ticket=intake,
        classification=classification,
        vendor=vendor,
        status=status,  # type: ignore[arg-type]
        tenant_sms=tenant_body,
        vendor_sms=vendor_sms["body"] if vendor_sms else None,
        airtable_record_id=airtable["id"],
    )
    return {
        "work_order": work_order.model_dump(mode="json"),
        "tenant_sms": tenant_sms,
        "vendor_sms": vendor_sms,
        "audit": [_audit("notify", {"work_order_id": wo_id, "status": status})],
    }


def build_graph():
    graph = StateGraph(TriageState)
    graph.add_node("classify", node_classify)
    graph.add_node("assign", node_assign)
    graph.add_node("notify", node_notify)
    graph.add_edge(START, "classify")
    graph.add_edge("classify", "assign")
    graph.add_edge("assign", "notify")
    graph.add_edge("notify", END)
    return graph.compile(checkpointer=InMemorySaver())


_APP = None


def run_triage(intake: TicketIntake | dict[str, Any]) -> AgentRun:
    global _APP
    if _APP is None:
        _APP = build_graph()
    ticket = intake if isinstance(intake, TicketIntake) else TicketIntake.model_validate(intake)
    thread = {"configurable": {"thread_id": str(uuid.uuid4())}}
    final = _APP.invoke({"intake": ticket.model_dump(mode="json"), "audit": []}, thread)
    return AgentRun(
        run_id=thread["configurable"]["thread_id"],
        agent=AgentName.TRIAGE,
        status="completed",
        finished_at=datetime.utcnow(),
        result=final.get("work_order") or {},
        audit=[AuditEvent.model_validate(a) for a in final.get("audit", [])],
        demo=True,
    )
