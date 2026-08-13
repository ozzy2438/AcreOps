from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from acreops.adapters.catalog import permits as catalog_permits
from acreops.schemas.permits import PermitRecord, PermitSnapshot, PermitStatus

# Simulated "last seen" store so a second poll can detect a change in demo mode.
_LAST_SEEN: dict[str, PermitStatus] = {}


def watched_permits() -> list[PermitRecord]:
    rows = catalog_permits()
    return [PermitRecord.model_validate(row) for row in rows]


def scrape_portal(record: PermitRecord, *, force_change: bool = False) -> PermitSnapshot:
    """Demo Selenium stand-in. Live mode would drive the city Accela/EnerGov portal."""
    status = _LAST_SEEN.get(record.permit_number, record.current_status)
    if force_change:
        nxt = {
            PermitStatus.SUBMITTED: PermitStatus.UNDER_REVIEW,
            PermitStatus.UNDER_REVIEW: PermitStatus.CORRECTIONS_REQUIRED,
            PermitStatus.CORRECTIONS_REQUIRED: PermitStatus.APPROVED,
            PermitStatus.APPROVED: PermitStatus.ISSUED,
            PermitStatus.ISSUED: PermitStatus.INSPECTION_SCHEDULED,
            PermitStatus.INSPECTION_SCHEDULED: PermitStatus.CERTIFICATE_ISSUED,
        }
        status = nxt.get(record.current_status, record.current_status)
    raw = f"{record.permit_number}:{status.value}:{record.portal_url}"
    next_action = {
        PermitStatus.CORRECTIONS_REQUIRED: "Respond to plan-check comments before the deadline.",
        PermitStatus.APPROVED: "Pay fees and pick up the issued permit.",
        PermitStatus.INSPECTION_SCHEDULED: "Confirm superintendent coverage for the inspection window.",
        PermitStatus.INSPECTION_FAILED: "Schedule re-inspection after punch items close.",
        PermitStatus.DENIED: "Review findings and decide appeal vs. redesign.",
        PermitStatus.EXPIRED: "File a renewal or extension immediately.",
    }.get(status)
    return PermitSnapshot(
        permit_number=record.permit_number,
        status=status,
        status_text=status.value.replace("_", " ").title(),
        captured_at=datetime.utcnow(),
        inspector_notes=record.notes or None,
        next_action=next_action,
        raw_html_hash=hashlib.sha256(raw.encode()).hexdigest()[:16],
    )


def detect_changes(
    records: list[PermitRecord], snapshots: list[PermitSnapshot]
) -> list[dict[str, Any]]:
    by_number = {s.permit_number: s for s in snapshots}
    changes: list[dict[str, Any]] = []
    for rec in records:
        snap = by_number.get(rec.permit_number)
        if not snap:
            continue
        previous = _LAST_SEEN.get(rec.permit_number, rec.current_status)
        if snap.status != previous:
            action_required = snap.status in {
                PermitStatus.CORRECTIONS_REQUIRED,
                PermitStatus.APPROVED,
                PermitStatus.INSPECTION_FAILED,
                PermitStatus.DENIED,
                PermitStatus.EXPIRED,
            }
            changes.append(
                {
                    "permit_number": rec.permit_number,
                    "project_name": rec.project_name,
                    "old_status": previous.value,
                    "new_status": snap.status.value,
                    "action_required": action_required,
                    "action_summary": snap.next_action
                    or f"Status moved {previous.value} → {snap.status.value}.",
                    "jurisdiction": rec.jurisdiction,
                    "portal_url": rec.portal_url,
                }
            )
        _LAST_SEEN[rec.permit_number] = snap.status
    return changes
