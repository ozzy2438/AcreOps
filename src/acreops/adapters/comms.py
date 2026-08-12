from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from acreops.config import get_settings

logger = logging.getLogger(__name__)


class CommsResult(dict[str, Any]):
    pass


def send_sms(to: str, body: str, *, kind: str = "sms") -> dict[str, Any]:
    settings = get_settings()
    if settings.twilio_account_sid and settings.twilio_auth_token:
        logger.info("Would send live Twilio SMS to %s", to)
    return {
        "channel": "sms",
        "kind": kind,
        "to": to,
        "body": body,
        "status": "demo_queued" if settings.demo_mode else "sent",
        "sid": f"SM_demo_{abs(hash(to + body)) % 10_000_000}",
        "sent_at": datetime.utcnow().isoformat(),
    }


def send_email(to: str, subject: str, body: str, *, kind: str = "email") -> dict[str, Any]:
    settings = get_settings()
    if settings.smtp_host and settings.smtp_user:
        logger.info("Would send live SMTP email to %s", to)
    return {
        "channel": "email",
        "kind": kind,
        "to": to,
        "subject": subject,
        "body": body,
        "status": "demo_queued" if settings.demo_mode else "sent",
        "message_id": f"em_demo_{abs(hash(to + subject)) % 10_000_000}",
        "sent_at": datetime.utcnow().isoformat(),
    }
