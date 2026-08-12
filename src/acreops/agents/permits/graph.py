from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from acreops.adapters.comms import send_email
from acreops.adapters.notion import upsert_timeline_event
from acreops.agents.permits.portal import detect_changes, scrape_portal, watched_permits
from acreops.config import get_settings
from acreops.schemas.common import AgentName, AgentRun, AuditEvent
from acreops.schemas.permits import StatusChange


class PermitState(TypedDict, total=False):
    force_change: bool
    snapshots: list[dict[str, Any]]
    changes: list[dict[str, Any]]
    notifications: list[dict[str, Any]]
    timeline: list[dict[str, Any]]
    audit: list[dict[str, Any]]


def _audit(action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return AuditEvent(agent=AgentName.PERMITS, action=action, payload=payload or {}).model_dump(
        mode="json"
    )


def node_poll(state: PermitState) -> dict[str, Any]:
    records = watched_permits()
    snapshots = [scrape_portal(r, force_change=bool(state.get("force_change"))) for r in records]
    return {
        "snapshots": [s.model_dump(mode="json") for s in snapshots],
        "audit": [_audit("poll_portals", {"count": len(snapshots)})],
    }


def node_diff(state: PermitState) -> dict[str, Any]:
    records = watched_permits()
    from acreops.schemas.permits import PermitSnapshot

    snapshots = [PermitSnapshot.model_validate(s) for s in state.get("snapshots", [])]
    changes = detect_changes(records, snapshots)
    return {
        "changes": changes,
        "audit": [_audit("detect_changes", {"count": len(changes)})],
    }


def node_notify(state: PermitState) -> dict[str, Any]:
    settings = get_settings()
    notifications = []
    timeline = []
    for change in state.get("changes", []):
        subject = (
            f"[Permit Pulse] {change['permit_number']} "
            f"{change['old_status']} → {change['new_status']}"
        )
        body = (
            f"Project: {change['project_name']}\n"
            f"Jurisdiction: {change['jurisdiction']}\n"
            f"Change: {change['old_status']} → {change['new_status']}\n"
            f"Action: {change['action_summary']}\n"
            f"Portal: {change['portal_url']}\n"
        )
        mail = send_email(settings.permit_alert_email, subject, body, kind="permit_alert")
        event = upsert_timeline_event(
            title=f"{change['permit_number']}: {change['new_status']}",
            status=change["new_status"],
            project=change["project_name"],
            permit_number=change["permit_number"],
            notes=change["action_summary"],
        )
        notifications.append(mail)
        timeline.append(event)
        change["email_sent"] = True
        change["notion_updated"] = True
    return {
        "changes": state.get("changes", []),
        "notifications": notifications,
        "timeline": timeline,
        "audit": [_audit("notify_and_timeline", {"emails": len(notifications)})],
    }


def build_graph():
    graph = StateGraph(PermitState)
    graph.add_node("poll", node_poll)
    graph.add_node("diff", node_diff)
    graph.add_node("notify", node_notify)
    graph.add_edge(START, "poll")
    graph.add_edge("poll", "diff")
    graph.add_edge("diff", "notify")
    graph.add_edge("notify", END)
    return graph.compile(checkpointer=InMemorySaver())


_APP = None


def run_permit_pulse(*, force_change: bool = True) -> AgentRun:
    global _APP
    if _APP is None:
        _APP = build_graph()
    thread = {"configurable": {"thread_id": str(uuid.uuid4())}}
    final = _APP.invoke({"force_change": force_change, "audit": []}, thread)
    changes = [StatusChange.model_validate(c) for c in final.get("changes", [])]
    return AgentRun(
        run_id=thread["configurable"]["thread_id"],
        agent=AgentName.PERMITS,
        status="completed",
        finished_at=datetime.utcnow(),
        result={
            "snapshots": final.get("snapshots", []),
            "changes": [c.model_dump(mode="json") for c in changes],
            "notifications": final.get("notifications", []),
            "timeline": final.get("timeline", []),
        },
        audit=[AuditEvent.model_validate(a) for a in final.get("audit", [])],
        demo=True,
    )
