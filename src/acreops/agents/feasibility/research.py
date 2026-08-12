from __future__ import annotations

from datetime import date

from acreops.adapters.catalog import find_parcel
from acreops.schemas.common import RiskTier
from acreops.schemas.feasibility import (
    CapacityScenario,
    CompSale,
    DemographicSnapshot,
    FeasibilityRequest,
    ZoningSummary,
)


def compile_zoning(request: FeasibilityRequest) -> ZoningSummary:
    parcel = find_parcel(request.address, request.parcel_id) or {}
    zoning = parcel.get("zoning", {})
    return ZoningSummary(
        jurisdiction=parcel.get("jurisdiction", f"{request.city}, {request.state}"),
        zone_code=zoning.get("zone_code", "MU-2"),
        zone_name=zoning.get("zone_name", "Mixed Use 2"),
        permitted_uses=zoning.get(
            "permitted_uses",
            ["multifamily", "ground-floor retail", "live-work"],
        ),
        conditional_uses=zoning.get("conditional_uses", ["hotel", "drive-through"]),
        max_height_ft=float(zoning.get("max_height_ft", 75)),
        max_far=float(zoning.get("max_far", 3.5)),
        max_density_du_acre=float(zoning.get("max_density_du_acre", 80)),
        front_setback_ft=float(zoning.get("front_setback_ft", 10)),
        side_setback_ft=float(zoning.get("side_setback_ft", 5)),
        rear_setback_ft=float(zoning.get("rear_setback_ft", 15)),
        parking_ratio=zoning.get("parking_ratio", "0.8 / unit + 2 / 1,000 sf retail"),
        overlays=zoning.get("overlays", []),
        flood_zone=zoning.get("flood_zone", "X"),
        opportunity_zone=bool(zoning.get("opportunity_zone", False)),
        source=zoning.get("source", "municipal zoning ordinance (demo catalog)"),
        citations=zoning.get(
            "citations",
            ["Municipal Code Ch. 17.24", "Zoning Map Sheet 14"],
        ),
    )


def compile_comps(request: FeasibilityRequest) -> list[CompSale]:
    parcel = find_parcel(request.address, request.parcel_id) or {}
    comps = []
    for row in parcel.get("comps", []):
        comps.append(
            CompSale(
                address=row["address"],
                sale_date=date.fromisoformat(row["sale_date"]),
                sale_price_usd=float(row["sale_price_usd"]),
                land_sf=float(row["land_sf"]),
                building_sf=row.get("building_sf"),
                price_psf=float(row["price_psf"]),
                units=row.get("units"),
                distance_mi=float(row["distance_mi"]),
                notes=row.get("notes", ""),
            )
        )
    if comps:
        return comps
    return [
        CompSale(
            address=f"210 {request.city} Ave",
            sale_date=date(2025, 11, 4),
            sale_price_usd=4_250_000,
            land_sf=22_000,
            building_sf=8_400,
            price_psf=193.18,
            units=18,
            distance_mi=0.4,
            notes="Value-add garden walk-up, similar zoning.",
        )
    ]


def compile_demographics(request: FeasibilityRequest) -> DemographicSnapshot:
    parcel = find_parcel(request.address, request.parcel_id) or {}
    demo = parcel.get("demographics", {})
    return DemographicSnapshot(
        geography=demo.get("geography", f"{request.city} 1-mile ring"),
        population=int(demo.get("population", 18420)),
        households=int(demo.get("households", 8120)),
        median_hh_income=float(demo.get("median_hh_income", 78600)),
        median_age=float(demo.get("median_age", 33.4)),
        renter_share=float(demo.get("renter_share", 0.61)),
        vacancy_rate=float(demo.get("vacancy_rate", 0.046)),
        employment_growth_5yr=float(demo.get("employment_growth_5yr", 0.084)),
        household_growth_5yr=float(demo.get("household_growth_5yr", 0.062)),
        source=demo.get("source", "ACS 5-year / local market intel (demo)"),
    )


def build_scenarios(
    request: FeasibilityRequest, zoning: ZoningSummary, comps: list[CompSale]
) -> list[CapacityScenario]:
    parcel = find_parcel(request.address, request.parcel_id) or {}
    acres = float(parcel.get("acres", 1.15))
    by_right_units = int(acres * zoning.max_density_du_acre)
    if request.target_units:
        by_right_units = min(by_right_units, request.target_units)
    avg_unit_sf = 850
    hard_cost_psf = 265
    rent_psf = max((c.price_psf * 0.007) for c in comps) if comps else 2.85
    rent_psf = min(max(rent_psf, 2.10), 4.80)

    def scenario(label: str, units: int, rent_mult: float, cost_mult: float) -> CapacityScenario:
        gsf = units * avg_unit_sf * 1.18
        stalls = int(round(units * 0.8))
        hard = gsf * hard_cost_psf * cost_mult
        noi = units * avg_unit_sf * rent_psf * rent_mult * 12 * 0.62
        residual = noi / 0.055 - hard * 1.22
        return CapacityScenario(
            label=label,
            units=units,
            gsf=round(gsf, 0),
            parking_stalls=stalls,
            estimated_hard_cost_usd=round(hard, 0),
            estimated_rent_psf=round(rent_psf * rent_mult, 2),
            noi_year1_usd=round(noi, 0),
            residual_land_value_usd=round(residual, 0),
        )

    return [
        scenario("By-right", max(by_right_units, 8), 1.0, 1.0),
        scenario("Density bonus / inclusionary", int(by_right_units * 1.2), 0.97, 1.06),
        scenario("Conservative absorption", int(by_right_units * 0.75), 0.93, 0.98),
    ]


def score_risk(
    zoning: ZoningSummary, scenarios: list[CapacityScenario], request: FeasibilityRequest
) -> tuple[RiskTier, list[str]]:
    notes: list[str] = []
    score = 0
    if request.intended_use not in " ".join(zoning.permitted_uses).lower():
        score += 2
        notes.append(f"Intended use '{request.intended_use}' is not clearly by-right.")
    if zoning.flood_zone not in {"X", "X500", "C"}:
        score += 2
        notes.append(f"Flood zone {zoning.flood_zone} requires elevation / insurance review.")
    if zoning.overlays:
        score += 1
        notes.append("Overlays present: " + ", ".join(zoning.overlays))
    residual = scenarios[0].residual_land_value_usd if scenarios else 0
    if request.land_price_usd and residual < request.land_price_usd:
        score += 2
        notes.append("Ask price sits above residual land value on the by-right case.")
    if score >= 4:
        return RiskTier.HIGH, notes or ["Multiple entitlement or underwriting flags."]
    if score >= 2:
        return RiskTier.MEDIUM, notes or ["Moderate diligence items remain."]
    return RiskTier.LOW, notes or ["By-right path looks clean on cataloged constraints."]


def write_summary(
    request: FeasibilityRequest,
    zoning: ZoningSummary,
    scenarios: list[CapacityScenario],
    risk_tier: RiskTier,
    notes: list[str],
) -> str:
    top = scenarios[0] if scenarios else None
    unit_line = f"{top.units} units / {int(top.gsf):,} GSF" if top else "n/a"
    return (
        f"{request.address}, {request.city} is zoned {zoning.zone_code} ({zoning.zone_name}) "
        f"in {zoning.jurisdiction}. By-right envelope supports {unit_line} at {zoning.max_far} FAR "
        f"and {zoning.max_height_ft:.0f} ft. Composite site risk is {risk_tier.value}. "
        + (" ".join(notes) if notes else "")
        + " Packet is assembled for broker review and counterparty signature."
    )
