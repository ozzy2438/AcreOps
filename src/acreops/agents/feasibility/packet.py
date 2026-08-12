from __future__ import annotations

from acreops.adapters.pandadoc import create_and_send_packet
from acreops.adapters.pdf import write_report
from acreops.schemas.feasibility import FeasibilityPacket


def render_pdf(packet: FeasibilityPacket) -> str:
    req = packet.request
    z = packet.zoning
    d = packet.demographics
    slug = req.address.lower().replace(" ", "-").replace(",", "")[:48]
    sections = [
        (
            "1. Executive summary",
            packet.executive_summary,
            None,
        ),
        (
            "2. Zoning envelope",
            f"Source: {z.source}. Citations: {', '.join(z.citations) or 'n/a'}.",
            [
                ["Item", "Standard"],
                ["Jurisdiction", z.jurisdiction],
                ["Zone", f"{z.zone_code} — {z.zone_name}"],
                ["Max height", f"{z.max_height_ft:.0f} ft"],
                ["Max FAR", f"{z.max_far}"],
                ["Max density", f"{z.max_density_du_acre:.0f} du/ac"],
                ["Setbacks F/S/R", f"{z.front_setback_ft}/{z.side_setback_ft}/{z.rear_setback_ft} ft"],
                ["Parking", z.parking_ratio],
                ["Flood / OZ", f"{z.flood_zone} / {'Yes' if z.opportunity_zone else 'No'}"],
                ["Overlays", ", ".join(z.overlays) or "None"],
                ["Permitted", ", ".join(z.permitted_uses)],
            ],
        ),
        (
            "3. Capacity scenarios",
            "Hard costs and residual land value are underwriting aids, not appraisals.",
            [["Scenario", "Units", "GSF", "Hard cost", "Yr-1 NOI", "Residual land"]]
            + [
                [
                    s.label,
                    str(s.units),
                    f"{int(s.gsf):,}",
                    f"${s.estimated_hard_cost_usd:,.0f}",
                    f"${s.noi_year1_usd:,.0f}",
                    f"${s.residual_land_value_usd:,.0f}",
                ]
                for s in packet.scenarios
            ],
        ),
        (
            "4. Sale comps",
            "Radius-filtered land / value-add comps from the market catalog.",
            [["Address", "Date", "Price", "PSF", "Mi"]]
            + [
                [
                    c.address,
                    c.sale_date.isoformat(),
                    f"${c.sale_price_usd:,.0f}",
                    f"${c.price_psf:,.0f}",
                    f"{c.distance_mi:.2f}",
                ]
                for c in packet.comps
            ],
        ),
        (
            "5. Demographics",
            f"Geography: {d.geography}. Source: {d.source}.",
            [
                ["Metric", "Value"],
                ["Population", f"{d.population:,}"],
                ["Households", f"{d.households:,}"],
                ["Median HH income", f"${d.median_hh_income:,.0f}"],
                ["Renter share", f"{d.renter_share:.0%}"],
                ["Vacancy", f"{d.vacancy_rate:.1%}"],
                ["5-yr HH growth", f"{d.household_growth_5yr:.1%}"],
                ["5-yr job growth", f"{d.employment_growth_5yr:.1%}"],
            ],
        ),
        (
            "6. Risk & next actions",
            f"Composite risk: {packet.risk_tier.value}. " + " ".join(packet.risk_notes),
            None,
        ),
    ]
    path = write_report(
        filename=f"feasibility-{slug}.pdf",
        title=f"Site Feasibility Kit — {req.address}",
        kicker=(
            f"{req.city}, {req.state} {req.zip_code}  ·  {req.intended_use.replace('_', ' ').title()}  ·  "
            f"Prepared for {req.broker_name}"
        ),
        sections=sections,
    )
    return str(path)


def send_pandadoc(packet: FeasibilityPacket) -> dict:
    recipients = []
    if packet.request.signer_email:
        first, _, last = (packet.request.signer_name or "Counterparty").partition(" ")
        recipients.append(
            {
                "email": packet.request.signer_email,
                "first_name": first or "Counterparty",
                "last_name": last or "",
                "role": "signer",
            }
        )
    recipients.append(
        {
            "email": packet.request.broker_email,
            "first_name": packet.request.broker_name.split(" ")[0],
            "last_name": " ".join(packet.request.broker_name.split(" ")[1:]) or "Desk",
            "role": "cc",
        }
    )
    return create_and_send_packet(
        name=f"LOI / Feasibility — {packet.request.address}",
        recipients=recipients,
        pdf_path=packet.pdf_path,
        metadata={
            "parcel": packet.request.parcel_id,
            "risk_tier": packet.risk_tier.value,
        },
    )
