from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from acreops.agents.feasibility.packet import render_pdf, send_pandadoc
from acreops.agents.feasibility.research import (
    build_scenarios,
    compile_comps,
    compile_demographics,
    compile_zoning,
    score_risk,
    write_summary,
)
from acreops.graphutil import AuditTrail
from acreops.schemas.common import AgentName, AgentRun, AuditEvent
from acreops.schemas.feasibility import FeasibilityPacket, FeasibilityRequest


class FeasibilityState(TypedDict, total=False):
    request: dict[str, Any]
    zoning: dict[str, Any]
    comps: list[dict[str, Any]]
    demographics: dict[str, Any]
    scenarios: list[dict[str, Any]]
    risk_tier: str
    risk_notes: list[str]
    executive_summary: str
    pdf_path: str
    pandadoc: dict[str, Any]
    audit: AuditTrail


def _audit(action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return AuditEvent(
        agent=AgentName.FEASIBILITY, action=action, payload=payload or {}
    ).model_dump(mode="json")


def node_zoning(state: FeasibilityState) -> dict[str, Any]:
    req = FeasibilityRequest.model_validate(state["request"])
    zoning = compile_zoning(req)
    return {
        "zoning": zoning.model_dump(mode="json"),
        "audit": [_audit("compile_zoning", {"zone": zoning.zone_code})],
    }


def node_comps(state: FeasibilityState) -> dict[str, Any]:
    req = FeasibilityRequest.model_validate(state["request"])
    comps = compile_comps(req)
    return {
        "comps": [c.model_dump(mode="json") for c in comps],
        "audit": [_audit("compile_comps", {"count": len(comps)})],
    }


def node_demographics(state: FeasibilityState) -> dict[str, Any]:
    req = FeasibilityRequest.model_validate(state["request"])
    demo = compile_demographics(req)
    return {
        "demographics": demo.model_dump(mode="json"),
        "audit": [_audit("compile_demographics", {"geography": demo.geography})],
    }


def node_underwrite(state: FeasibilityState) -> dict[str, Any]:
    req = FeasibilityRequest.model_validate(state["request"])
    from acreops.schemas.feasibility import CompSale, ZoningSummary

    zoning = ZoningSummary.model_validate(state["zoning"])
    comps = [CompSale.model_validate(c) for c in state["comps"]]
    scenarios = build_scenarios(req, zoning, comps)
    tier, notes = score_risk(zoning, scenarios, req)
    summary = write_summary(req, zoning, scenarios, tier, notes)
    return {
        "scenarios": [s.model_dump(mode="json") for s in scenarios],
        "risk_tier": tier.value,
        "risk_notes": notes,
        "executive_summary": summary,
        "audit": [_audit("underwrite", {"risk_tier": tier.value})],
    }


def node_packet(state: FeasibilityState) -> dict[str, Any]:
    packet = FeasibilityPacket.model_validate(
        {
            "request": state["request"],
            "zoning": state["zoning"],
            "comps": state["comps"],
            "demographics": state["demographics"],
            "scenarios": state["scenarios"],
            "risk_tier": state["risk_tier"],
            "risk_notes": state["risk_notes"],
            "executive_summary": state["executive_summary"],
        }
    )
    pdf_path = render_pdf(packet)
    packet.pdf_path = pdf_path
    doc = send_pandadoc(packet)
    return {
        "pdf_path": pdf_path,
        "pandadoc": doc,
        "audit": [_audit("assemble_packet", {"pdf": pdf_path, "pandadoc_id": doc["id"]})],
    }


def build_graph():
    graph = StateGraph(FeasibilityState)
    graph.add_node("zoning", node_zoning)
    graph.add_node("comps", node_comps)
    graph.add_node("demographics", node_demographics)
    graph.add_node("underwrite", node_underwrite)
    graph.add_node("packet", node_packet)
    graph.add_edge(START, "zoning")
    graph.add_edge("zoning", "comps")
    graph.add_edge("comps", "demographics")
    graph.add_edge("demographics", "underwrite")
    graph.add_edge("underwrite", "packet")
    graph.add_edge("packet", END)
    return graph.compile(checkpointer=InMemorySaver())


_APP = None


def run_feasibility(request: FeasibilityRequest | dict[str, Any]) -> AgentRun:
    global _APP
    if _APP is None:
        _APP = build_graph()
    req = request if isinstance(request, FeasibilityRequest) else FeasibilityRequest.model_validate(request)
    thread = {"configurable": {"thread_id": str(uuid.uuid4())}}
    final = _APP.invoke({"request": req.model_dump(mode="json"), "audit": []}, thread)
    packet = FeasibilityPacket.model_validate(
        {
            "request": final["request"],
            "zoning": final["zoning"],
            "comps": final["comps"],
            "demographics": final["demographics"],
            "scenarios": final["scenarios"],
            "risk_tier": final["risk_tier"],
            "risk_notes": final["risk_notes"],
            "executive_summary": final["executive_summary"],
            "pdf_path": final.get("pdf_path"),
            "pandadoc_document_id": (final.get("pandadoc") or {}).get("id"),
            "pandadoc_status": (final.get("pandadoc") or {}).get("status"),
            "ready_to_sign": True,
        }
    )
    return AgentRun(
        run_id=thread["configurable"]["thread_id"],
        agent=AgentName.FEASIBILITY,
        status="completed",
        finished_at=datetime.utcnow(),
        result=packet.model_dump(mode="json"),
        audit=[AuditEvent.model_validate(a) for a in final.get("audit", [])],
        demo=True,
    )
