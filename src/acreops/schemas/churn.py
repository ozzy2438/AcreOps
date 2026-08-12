from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field

from acreops.schemas.common import RiskTier


class ChurnDriver(str, Enum):
    PRICE = "price"
    MAINTENANCE = "maintenance"
    MARKET = "market"
    LIFE_EVENT = "life_event"
    SATISFACTION = "satisfaction"
    PAYMENT_STRESS = "payment_stress"
    UNKNOWN = "unknown"


class TenantLease(BaseModel):
    tenant_id: str
    tenant_name: str
    tenant_email: str
    unit_id: str
    property_id: str
    property_name: str
    monthly_rent: float
    market_rent: float
    lease_start: date
    lease_end: date
    tenure_months: int
    prior_renewals: int
    late_payment_ratio: float
    nsf_count_12m: int = 0
    open_work_orders: int = 0
    avg_maintenance_days: float = 3.0
    unresolved_work_orders: int = 0
    portal_logins_30d: int = 4
    csat: float | None = None
    auto_pay: bool = True
    neighborhood_vacancy: float = 0.05
    building_recent_moveouts: int = 0
    rent_increase_offered_pct: float = 0.03


class ChurnPrediction(BaseModel):
    tenant_id: str
    tenant_name: str
    property_name: str
    unit_id: str
    lease_end: date
    days_to_expiry: int
    churn_probability: float
    risk_tier: RiskTier
    primary_driver: ChurnDriver
    drivers: dict[str, float] = Field(default_factory=dict)
    recommended_incentive: str
    estimated_turnover_cost: float
    incentive_budget: float
    feature_importance: dict[str, float] = Field(default_factory=dict)


class IncentiveOffer(BaseModel):
    offer_id: str
    tenant_id: str
    subject: str
    body: str
    incentive_type: str
    incentive_value_usd: float
    valid_until: date
    email_sent: bool = False
    sent_at: datetime | None = None
