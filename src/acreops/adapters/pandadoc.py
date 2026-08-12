from __future__ import annotations

from datetime import datetime
from typing import Any

from acreops.config import get_settings


def create_and_send_packet(
    name: str,
    recipients: list[dict[str, str]],
    pdf_path: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a PandaDoc packet. Demo mode returns a ready-to-sign stub."""
    settings = get_settings()
    doc_id = f"pd_{abs(hash(name + str(recipients))) % 10_000_000:07d}"
    if settings.pandadoc_api_key:
        status = "document.draft"
        note = "Live PandaDoc key present — wire create_document + send_document here."
    else:
        status = "document.draft"
        note = "Demo packet assembled. Connect PANDADOC_API_KEY to send for signature."
    return {
        "id": doc_id,
        "name": name,
        "status": status,
        "recipients": recipients,
        "pdf_path": pdf_path,
        "metadata": metadata or {},
        "ready_to_sign": True,
        "share_url": f"https://app.pandadoc.com/document/v1/{doc_id}",
        "created_at": datetime.utcnow().isoformat(),
        "note": note,
    }
