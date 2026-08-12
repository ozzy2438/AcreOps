from __future__ import annotations

from datetime import date

import pandas as pd

from acreops.schemas.churn import TenantLease

FEATURE_COLUMNS = [
    "days_to_expiry",
    "tenure_months",
    "prior_renewals",
    "late_payment_ratio",
    "nsf_count_12m",
    "open_work_orders",
    "avg_maintenance_days",
    "unresolved_work_orders",
    "portal_logins_30d",
    "csat",
    "auto_pay",
    "neighborhood_vacancy",
    "building_recent_moveouts",
    "rent_to_market",
    "rent_increase_offered_pct",
    "monthly_rent",
]


def days_to_expiry(lease_end: date, today: date | None = None) -> int:
    today = today or date.today()
    return (lease_end - today).days


def feature_frame(leases: list[TenantLease], today: date | None = None) -> pd.DataFrame:
    rows = []
    for lease in leases:
        rows.append(
            {
                "tenant_id": lease.tenant_id,
                "days_to_expiry": days_to_expiry(lease.lease_end, today),
                "tenure_months": lease.tenure_months,
                "prior_renewals": lease.prior_renewals,
                "late_payment_ratio": lease.late_payment_ratio,
                "nsf_count_12m": lease.nsf_count_12m,
                "open_work_orders": lease.open_work_orders,
                "avg_maintenance_days": lease.avg_maintenance_days,
                "unresolved_work_orders": lease.unresolved_work_orders,
                "portal_logins_30d": lease.portal_logins_30d,
                "csat": lease.csat if lease.csat is not None else 3.5,
                "auto_pay": int(lease.auto_pay),
                "neighborhood_vacancy": lease.neighborhood_vacancy,
                "building_recent_moveouts": lease.building_recent_moveouts,
                "rent_to_market": lease.monthly_rent / max(lease.market_rent, 1),
                "rent_increase_offered_pct": lease.rent_increase_offered_pct,
                "monthly_rent": lease.monthly_rent,
            }
        )
    return pd.DataFrame(rows)
