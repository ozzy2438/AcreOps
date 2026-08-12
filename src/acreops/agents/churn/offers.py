from __future__ import annotations

from datetime import date, timedelta

from acreops.schemas.churn import ChurnDriver, ChurnPrediction, IncentiveOffer, TenantLease
from acreops.schemas.common import RiskTier

TURNOVER_COST = 4200.0


def risk_tier(prob: float) -> RiskTier:
    if prob >= 0.72:
        return RiskTier.CRITICAL
    if prob >= 0.55:
        return RiskTier.HIGH
    if prob >= 0.35:
        return RiskTier.MEDIUM
    return RiskTier.LOW


def primary_driver(lease: TenantLease) -> tuple[ChurnDriver, str, float]:
    rent_gap = lease.monthly_rent / max(lease.market_rent, 1) - 1
    if lease.unresolved_work_orders >= 1 or lease.avg_maintenance_days >= 7:
        return (
            ChurnDriver.MAINTENANCE,
            "Priority maintenance + $150 amenity credit",
            150,
        )
    if lease.late_payment_ratio >= 0.18 or lease.nsf_count_12m >= 2:
        return (
            ChurnDriver.PAYMENT_STRESS,
            "Split the increase over 6 months + late-fee waiver",
            180,
        )
    if rent_gap >= 0.06 or lease.rent_increase_offered_pct >= 0.06:
        return ChurnDriver.PRICE, "Cap renewal increase at 2% or $75/mo concession", 75 * 12
    if lease.building_recent_moveouts >= 2 or lease.neighborhood_vacancy >= 0.08:
        return ChurnDriver.MARKET, "Match nearby special: 6 weeks free equivalent as $400 gift", 400
    if lease.csat is not None and lease.csat <= 3.2:
        return ChurnDriver.SATISFACTION, "Resident success call + parking upgrade", 80
    return ChurnDriver.UNKNOWN, "Standard renewal + $50 gift card", 50


def draft_offer(lease: TenantLease, prediction: ChurnPrediction) -> IncentiveOffer:
    first = lease.tenant_name.split()[0]
    subject = f"Your {lease.property_name} renewal — we saved something for you"
    body = (
        f"Hi {first},\n\n"
        f"Your lease at {lease.property_name} unit {lease.unit_id} ends "
        f"{lease.lease_end.isoformat()} ({prediction.days_to_expiry} days). "
        f"We'd like you to stay.\n\n"
        f"Recommended offer ({prediction.primary_driver.value}): "
        f"{prediction.recommended_incentive}.\n\n"
        f"This is worth about ${prediction.incentive_budget:,.0f} against an estimated "
        f"${prediction.estimated_turnover_cost:,.0f} make-ready and vacancy cost.\n\n"
        f"Reply YES and we'll send the formal PandaDoc renewal.\n\n"
        f"— AcreOps Renewals"
    )
    return IncentiveOffer(
        offer_id=f"OFF-{lease.tenant_id}-{prediction.days_to_expiry}",
        tenant_id=lease.tenant_id,
        subject=subject,
        body=body,
        incentive_type=prediction.primary_driver.value,
        incentive_value_usd=prediction.incentive_budget,
        valid_until=date.today() + timedelta(days=21),
    )
