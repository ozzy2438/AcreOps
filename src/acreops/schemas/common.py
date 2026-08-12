from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentName(str, Enum):
    FEASIBILITY = "site_feasibility"
    TRIAGE = "tenant_triage"
    PERMITS = "permit_pulse"
    DRONE = "drone_progress"
    CHURN = "lease_churn"


class AuditEvent(BaseModel):
    agent: AgentName
    action: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actor: str = "agent"
    payload: dict[str, Any] = Field(default_factory=dict)
    human_approved: bool | None = None


class AgentRun(BaseModel):
    run_id: str
    agent: AgentName
    status: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None
    result: dict[str, Any] = Field(default_factory=dict)
    audit: list[AuditEvent] = Field(default_factory=list)
    demo: bool = True
