from __future__ import annotations

from acreops.adapters.airtable import list_vendors
from acreops.schemas.triage import TicketClassification, TicketIntake, Vendor

ZONE_BY_PROPERTY = {
    "oak-ridge": "north",
    "harbor-lofts": "central",
    "cedar-court": "south",
    "midtown-flats": "central",
}


def property_zone(property_id: str) -> str:
    return ZONE_BY_PROPERTY.get(property_id, "central")


def select_vendor(intake: TicketIntake, classification: TicketClassification) -> Vendor | None:
    if classification.tenant_responsibility:
        return None
    zone = property_zone(intake.property_id)
    rows = list_vendors(trade=classification.trade.value, zone=zone)
    if not rows:
        rows = list_vendors(trade=classification.trade.value)
    if classification.severity.value == "emergency":
        rows = [r for r in rows if r.get("emergency_available")] or rows
    if not rows:
        return None
    row = rows[0]
    return Vendor.model_validate(row)
