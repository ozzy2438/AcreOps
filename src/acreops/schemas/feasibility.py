from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from acreops.schemas.common import RiskTier


class FeasibilityRequest(BaseModel):
    address: str
    city: str
    state: str
    zip_code: str
    parcel_id: str | None = None
    intended_use: Literal[
        "multifamily", "mixed_use", "industrial", "office", "retail", "single_family"
    ] = "multifamily"
    target_units: int | None = None
    land_price_usd: float | None = None
    broker_name: str = "AcreOps Broker Desk"
    broker_email: str = "broker@acreops.local"
    signer_name: str | None = None
    signer_email: str | None = None


class ZoningSummary(BaseModel):
    jurisdiction: str
    zone_code: str
    zone_name: str
    permitted_uses: list[str]
    conditional_uses: list[str] = Field(default_factory=list)
    max_height_ft: float
    max_far: float
    max_density_du_acre: float
    front_setback_ft: float
    side_setback_ft: float
    rear_setback_ft: float
    parking_ratio: str
    overlays: list[str] = Field(default_factory=list)
    flood_zone: str = "X"
    opportunity_zone: bool = False
    source: str = "municipal zoning ordinance (demo catalog)"
    citations: list[str] = Field(default_factory=list)


class CompSale(BaseModel):
    address: str
    sale_date: date
    sale_price_usd: float
    land_sf: float
    building_sf: float | None = None
    price_psf: float
    units: int | None = None
    distance_mi: float
    notes: str = ""


class DemographicSnapshot(BaseModel):
    geography: str
    population: int
    households: int
    median_hh_income: float
    median_age: float
    renter_share: float
    vacancy_rate: float
    employment_growth_5yr: float
    household_growth_5yr: float
    source: str = "ACS 5-year / local market intel (demo)"


class CapacityScenario(BaseModel):
    label: str
    units: int
    gsf: float
    parking_stalls: int
    estimated_hard_cost_usd: float
    estimated_rent_psf: float
    noi_year1_usd: float
    residual_land_value_usd: float


class FeasibilityPacket(BaseModel):
    request: FeasibilityRequest
    zoning: ZoningSummary
    comps: list[CompSale]
    demographics: DemographicSnapshot
    scenarios: list[CapacityScenario]
    risk_tier: RiskTier
    risk_notes: list[str]
    executive_summary: str
    pdf_path: str | None = None
    pandadoc_document_id: str | None = None
    pandadoc_status: str | None = None
    ready_to_sign: bool = False
