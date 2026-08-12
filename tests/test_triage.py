from acreops.agents.triage.classifier import classify_ticket
from acreops.agents.triage.graph import run_triage
from acreops.schemas.triage import TicketIntake


def _intake(description: str, property_id: str = "harbor-lofts") -> TicketIntake:
    return TicketIntake(
        tenant_name="Alex Rivera",
        tenant_phone="+15125550001",
        unit_id="4B",
        property_id=property_id,
        address="88 Harbor Way",
        description=description,
    )


def test_emergency_burst_pipe():
    clf = classify_ticket(_intake("burst pipe flooding the kitchen"))
    assert clf.severity.value == "emergency"
    assert clf.trade.value == "plumbing"
    assert clf.sla_hours == 2


def test_tenant_responsibility_bulb():
    clf = classify_ticket(_intake("need a new light bulb in the hallway"))
    assert clf.tenant_responsibility is True
    assert clf.recommended_action == "reply_self_help"


def test_triage_assigns_plumber():
    run = run_triage(_intake("Kitchen sink is leaking and water is pooling on the floor"))
    wo = run.result
    assert wo["classification"]["trade"] == "plumbing"
    assert wo["vendor"]["trade"] == "plumbing"
    assert wo["status"] == "dispatched"
    assert "Rio Grande" in wo["vendor"]["name"] or wo["vendor"]["phone"]
