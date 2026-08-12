from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PermitStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    CORRECTIONS_REQUIRED = "corrections_required"
    APPROVED = "approved"
    ISSUED = "issued"
    INSPECTION_SCHEDULED = "inspection_scheduled"
    INSPECTION_FAILED = "inspection_failed"
    CERTIFICATE_ISSUED = "certificate_issued"
    DENIED = "denied"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"


class PermitRecord(BaseModel):
    permit_number: str
    project_name: str
    address: str
    jurisdiction: str
    portal_url: str
    permit_type: str
    applicant: str
    current_status: PermitStatus
    last_checked_at: datetime | None = None
    response_deadline: datetime | None = None
    expiration_date: datetime | None = None
    notion_page_id: str | None = None
    notes: str = ""


class PermitSnapshot(BaseModel):
    permit_number: str
    status: PermitStatus
    status_text: str
    captured_at: datetime = Field(default_factory=datetime.utcnow)
    inspector_notes: str | None = None
    next_action: str | None = None
    raw_html_hash: str | None = None


class StatusChange(BaseModel):
    permit_number: str
    project_name: str
    old_status: PermitStatus
    new_status: PermitStatus
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    action_required: bool
    action_summary: str
    email_sent: bool = False
    notion_updated: bool = False
    days_in_previous_status: int | None = None
