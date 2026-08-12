from __future__ import annotations

import re

from acreops.schemas.triage import Severity, TicketClassification, TicketIntake, Trade

EMERGENCY_PATTERNS = [
    r"flood|flooding|water everywhere|burst pipe|sewage|gas smell|gas leak",
    r"no heat|no heating|sparking|sparks|smoke|fire|carbon monoxide",
    r"broken (exterior )?door lock|can't lock|cannot lock|lock broken outside",
    r"exposed wire|electrical fire",
]
URGENT_PATTERNS = [
    r"no hot water|no ac|no a/c|air condition",
    r"only (bathroom|toilet).*(not|won't|broken)|toilet.*(overflow|backed)",
    r"fridge|refrigerator.*(warm|not cool)|pest|roaches|bed ?bug|mice",
    r"dishwasher|not draining|won't drain",
    r"leak(?!y faucet)|leaking",
]
TENANT_PATTERNS = [
    r"light ?bulb|ac filter|air filter|lockout|lost (my )?key|clogged from grease",
]
# Specific trades first so "dishwasher not draining" is appliance, not plumbing.
TRADE_MAP: list[tuple[str, Trade]] = [
    (r"fridge|dishwasher|washer|dryer|stove|oven|appliance", Trade.APPLIANCE),
    (r"lock|key|door lock", Trade.LOCKSMITH),
    (r"pest|roach|bug|mice|rat|ant", Trade.PEST),
    (r"plumb|leak|drain|toilet|sewage|pipe|faucet|water heater", Trade.PLUMBING),
    (r"heat|hvac|ac\b|a/c|furnace|thermostat|air condition", Trade.HVAC),
    (r"electric|outlet|breaker|spark|wire|power out", Trade.ELECTRICAL),
]

SLA = {
    Severity.EMERGENCY: 2,
    Severity.URGENT: 8,
    Severity.ROUTINE: 48,
    Severity.TENANT_RESPONSIBILITY: 120,
}
ACTION = {
    Severity.EMERGENCY: "dispatch_emergency_vendor",
    Severity.URGENT: "dispatch_same_day_vendor",
    Severity.ROUTINE: "schedule_routine_vendor",
    Severity.TENANT_RESPONSIBILITY: "reply_self_help",
}


def _match(patterns: list[str], text: str) -> bool:
    return any(re.search(p, text, flags=re.I) for p in patterns)


def classify_ticket(intake: TicketIntake) -> TicketClassification:
    text = intake.description.lower()
    if _match(EMERGENCY_PATTERNS, text):
        severity = Severity.EMERGENCY
    elif _match(TENANT_PATTERNS, text) and not _match(URGENT_PATTERNS, text):
        severity = Severity.TENANT_RESPONSIBILITY
    elif _match(URGENT_PATTERNS, text):
        severity = Severity.URGENT
    else:
        severity = Severity.ROUTINE

    trade = Trade.GENERAL
    for pattern, mapped in TRADE_MAP:
        if re.search(pattern, text, flags=re.I):
            trade = mapped
            break

    reasoning = (
        f"Rule classifier read '{intake.description[:160]}' and scored "
        f"{severity.value}/{trade.value}. Emergencies dispatch immediately; "
        f"tenant-responsibility items get a lease-clause self-help reply."
    )
    return TicketClassification(
        severity=severity,
        trade=trade,
        sla_hours=SLA[severity],
        accommodation_flag=bool(re.search(r"accessib|ada|disability|mobility", text)),
        weather_relevant=bool(re.search(r"heat|ac\b|a/c|freeze|snow|flood", text)),
        tenant_responsibility=severity is Severity.TENANT_RESPONSIBILITY,
        reasoning=reasoning,
        recommended_action=ACTION[severity],  # type: ignore[arg-type]
        confidence=0.86 if severity is not Severity.ROUTINE else 0.78,
    )
