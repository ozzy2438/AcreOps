from __future__ import annotations

from datetime import datetime
from typing import Any

from acreops.config import get_settings

_TIMELINE: list[dict[str, Any]] = []


def upsert_timeline_event(
    title: str,
    status: str,
    project: str,
    permit_number: str,
    notes: str = "",
    page_id: str | None = None,
) -> dict[str, Any]:
    settings = get_settings()
    event = {
        "page_id": page_id or f"ntn_{abs(hash(permit_number + status)) % 10_000_000:07d}",
        "title": title,
        "status": status,
        "project": project,
        "permit_number": permit_number,
        "notes": notes,
        "updated_at": datetime.utcnow().isoformat(),
        "database_id": settings.notion_timeline_database_id or "demo-timeline",
        "live": bool(settings.notion_api_key),
    }
    _TIMELINE.append(event)
    return event


def recent_timeline(limit: int = 20) -> list[dict[str, Any]]:
    return list(reversed(_TIMELINE[-limit:]))
