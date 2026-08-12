from __future__ import annotations

from datetime import datetime
from typing import Any

from acreops.adapters.catalog import vendors as catalog_vendors
from acreops.config import get_settings


def list_vendors(trade: str | None = None, zone: str | None = None) -> list[dict[str, Any]]:
    settings = get_settings()
    if settings.airtable_api_key and settings.airtable_base_id:
        # Live path is intentionally a stub so the demo never calls Airtable.
        pass
    rows = catalog_vendors()
    out = []
    for row in rows:
        if trade and row.get("trade") != trade:
            continue
        if zone and row.get("zone") != zone and row.get("zone") != "all":
            continue
        if row.get("status", "active") != "active":
            continue
        out.append(row)
    out.sort(key=lambda r: (-float(r.get("rating", 0)), int(r.get("avg_response_min", 999))))
    return out


def upsert_work_order(payload: dict[str, Any]) -> dict[str, Any]:
    record_id = f"rec{abs(hash(str(payload))) % 10_000_000:07d}"
    return {
        "id": record_id,
        "fields": payload,
        "createdTime": datetime.utcnow().isoformat(),
        "source": "airtable_demo",
    }
