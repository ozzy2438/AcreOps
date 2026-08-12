from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class ElementStatus(str, Enum):
    COMPLETE = "complete"
    IN_PROGRESS = "in_progress"
    NOT_STARTED = "not_started"
    DELAYED = "delayed"
    AHEAD = "ahead"
    OCCLUDED = "occluded"


class DiscrepancySeverity(str, Enum):
    INFO = "info"
    WATCH = "watch"
    MATERIAL = "material"
    CRITICAL = "critical"


class BimElement(BaseModel):
    element_id: str
    name: str
    discipline: str
    planned_pct: float
    planned_volume_m3: float | None = None
    scheduled_start: date | None = None
    scheduled_finish: date | None = None
    location: str = ""


class ProgressEstimate(BaseModel):
    element_id: str
    name: str
    planned_pct: float
    observed_pct: float
    delta_pct: float
    status: ElementStatus
    confidence: float
    evidence: str
    occlusion: bool = False


class Discrepancy(BaseModel):
    element_id: str
    name: str
    severity: DiscrepancySeverity
    kind: str
    description: str
    recommended_action: str
    requires_superintendent: bool = True


class DroneReport(BaseModel):
    report_id: str
    project_name: str
    flight_date: date
    overall_planned_pct: float
    overall_observed_pct: float
    schedule_delta_days: float
    elements: list[ProgressEstimate]
    discrepancies: list[Discrepancy]
    narrative: str
    superintendent_validated: bool = False
    superintendent_notes: str | None = None
    schedule_updated: bool = False
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    pdf_path: str | None = None
