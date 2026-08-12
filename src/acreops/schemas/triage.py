from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Severity(str, Enum):
    EMERGENCY = "emergency"
    URGENT = "urgent"
    ROUTINE = "routine"
    TENANT_RESPONSIBILITY = "tenant_responsibility"


class Trade(str, Enum):
    PLUMBING = "plumbing"
    HVAC = "hvac"
    ELECTRICAL = "electrical"
    APPLIANCE = "appliance"
    GENERAL = "general"
    LOCKSMITH = "locksmith"
    PEST = "pest"
    OTHER = "other"


class TicketIntake(BaseModel):
    source: Literal["appfolio", "email", "sms", "portal"] = "appfolio"
    tenant_name: str
    tenant_phone: str | None = None
    tenant_email: str | None = None
    unit_id: str
    property_id: str
    address: str
    description: str
    photos: list[str] = Field(default_factory=list)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    language: str = "en"


class TicketClassification(BaseModel):
    severity: Severity
    trade: Trade
    sla_hours: int
    accommodation_flag: bool = False
    duplicate_of: str | None = None
    weather_relevant: bool = False
    tenant_responsibility: bool = False
    reasoning: str
    recommended_action: Literal[
        "dispatch_emergency_vendor",
        "dispatch_same_day_vendor",
        "schedule_routine_vendor",
        "reply_self_help",
        "human_review",
    ]
    confidence: float = 0.9


class Vendor(BaseModel):
    vendor_id: str
    name: str
    trade: Trade
    phone: str
    email: str
    zone: str
    rating: float
    emergency_available: bool
    avg_response_min: int
    status: Literal["active", "paused"] = "active"
    last_assigned_at: datetime | None = None
    insurance_expires: datetime | None = None


class WorkOrder(BaseModel):
    work_order_id: str
    ticket: TicketIntake
    classification: TicketClassification
    vendor: Vendor | None = None
    status: Literal[
        "triaged", "assigned", "dispatched", "en_route", "complete", "needs_human"
    ] = "triaged"
    tenant_sms: str | None = None
    vendor_sms: str | None = None
    airtable_record_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
