from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from acreops.adapters.catalog import tenants as catalog_tenants
from acreops.adapters.comms import send_email
from acreops.agents.churn.features import FEATURE_COLUMNS, days_to_expiry, feature_frame
from acreops.agents.churn.offers import TURNOVER_COST, draft_offer, primary_driver, risk_tier
from acreops.agents.churn.train import load_or_train
from acreops.config import get_settings
from acreops.schemas.churn import ChurnPrediction, TenantLease
from acreops.schemas.common import AgentName, AgentRun, AuditEvent


class ChurnState(TypedDict, total=False):
    horizon_days: int
    min_probability: float
    send_email: bool
    predictions: list[dict[str, Any]]
    offers: list[dict[str, Any]]
    emails: list[dict[str, Any]]
    audit: list[dict[str, Any]]


def _audit(action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return AuditEvent(agent=AgentName.CHURN, action=action, payload=payload or {}).model_dump(
        mode="json"
    )


def load_leases() -> list[TenantLease]:
    return [TenantLease.model_validate(row) for row in catalog_tenants()]


def node_score(state: ChurnState) -> dict[str, Any]:
    leases = load_leases()
    today = date.today()
    horizon = int(state.get("horizon_days") or 90)
    floor = float(state.get("min_probability") or 0.35)
    booster = load_or_train()
    frame = feature_frame(leases, today)
    probs = booster.predict(frame[FEATURE_COLUMNS])
    importance = dict(
        zip(FEATURE_COLUMNS, (float(x) for x in booster.feature_importance(importance_type="gain")))
    )
    total = sum(importance.values()) or 1.0
    importance = {k: round(v / total, 3) for k, v in importance.items()}

    predictions: list[dict[str, Any]] = []
    by_id = {lease.tenant_id: lease for lease in leases}
    for tenant_id, prob in zip(frame["tenant_id"], probs):
        lease = by_id[tenant_id]
        dte = days_to_expiry(lease.lease_end, today)
        if dte < 0 or dte > horizon:
            continue
        if float(prob) < floor:
            continue
        driver, incentive, budget = primary_driver(lease)
        pred = ChurnPrediction(
            tenant_id=lease.tenant_id,
            tenant_name=lease.tenant_name,
            property_name=lease.property_name,
            unit_id=lease.unit_id,
            lease_end=lease.lease_end,
            days_to_expiry=dte,
            churn_probability=round(float(prob), 3),
            risk_tier=risk_tier(float(prob)),
            primary_driver=driver,
            recommended_incentive=incentive,
            estimated_turnover_cost=TURNOVER_COST,
            incentive_budget=float(budget),
            feature_importance=importance,
        )
        predictions.append(pred.model_dump(mode="json"))
    predictions.sort(key=lambda p: p["churn_probability"], reverse=True)
    return {
        "predictions": predictions,
        "audit": [_audit("score_portfolio", {"flagged": len(predictions)})],
    }


def node_offers(state: ChurnState) -> dict[str, Any]:
    leases = {lease.tenant_id: lease for lease in load_leases()}
    offers = []
    emails = []
    settings = get_settings()
    for raw in state.get("predictions", []):
        pred = ChurnPrediction.model_validate(raw)
        lease = leases[pred.tenant_id]
        offer = draft_offer(lease, pred)
        if state.get("send_email", True):
            mail = send_email(
                lease.tenant_email,
                offer.subject,
                offer.body,
                kind="renewal_incentive",
            )
            offer.email_sent = True
            offer.sent_at = datetime.utcnow()
            emails.append(mail)
        offers.append(offer.model_dump(mode="json"))
    return {
        "offers": offers,
        "emails": emails,
        "audit": [
            _audit(
                "send_incentives",
                {"offers": len(offers), "from": settings.churn_from_email},
            )
        ],
    }


def build_graph():
    graph = StateGraph(ChurnState)
    graph.add_node("score", node_score)
    graph.add_node("offers", node_offers)
    graph.add_edge(START, "score")
    graph.add_edge("score", "offers")
    graph.add_edge("offers", END)
    return graph.compile(checkpointer=InMemorySaver())


_APP = None


def run_churn_sweep(
    horizon_days: int = 90, min_probability: float = 0.35, send_email: bool = True
) -> AgentRun:
    global _APP
    if _APP is None:
        _APP = build_graph()
    thread = {"configurable": {"thread_id": str(uuid.uuid4())}}
    final = _APP.invoke(
        {
            "horizon_days": horizon_days,
            "min_probability": min_probability,
            "send_email": send_email,
            "audit": [],
        },
        thread,
    )
    return AgentRun(
        run_id=thread["configurable"]["thread_id"],
        agent=AgentName.CHURN,
        status="completed",
        finished_at=datetime.utcnow(),
        result={
            "predictions": final.get("predictions", []),
            "offers": final.get("offers", []),
            "emails": final.get("emails", []),
        },
        audit=[AuditEvent.model_validate(a) for a in final.get("audit", [])],
        demo=True,
    )
