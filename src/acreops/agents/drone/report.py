from __future__ import annotations

from acreops.adapters.pdf import write_report
from acreops.schemas.drone import DroneReport


def render_progress_pdf(report: DroneReport) -> str:
    slug = report.project_name.lower().replace(" ", "-")[:40]
    sections = [
        (
            "1. Field narrative",
            report.narrative,
            [
                ["Metric", "Value"],
                ["Planned overall", f"{report.overall_planned_pct:.1f}%"],
                ["Observed overall", f"{report.overall_observed_pct:.1f}%"],
                ["Schedule delta", f"{report.schedule_delta_days:+.1f} days"],
                ["Flagged discrepancies", str(len(report.discrepancies))],
                [
                    "Superintendent",
                    "Validated" if report.superintendent_validated else "Awaiting validation",
                ],
            ],
        ),
        (
            "2. Element progress vs. BIM",
            "Observed % is a vision estimate against the 4D planned envelope. Occluded elements are excluded from schedule updates.",
            [["Element", "Planned", "Observed", "Δ pp", "Status", "Conf."]]
            + [
                [
                    e.name,
                    f"{e.planned_pct:.0f}%",
                    f"{e.observed_pct:.0f}%",
                    f"{e.delta_pct:+.0f}",
                    e.status.value,
                    f"{e.confidence:.2f}",
                ]
                for e in report.elements
            ],
        ),
        (
            "3. Flagged discrepancies",
            "Nothing here writes the master schedule until a superintendent validates.",
            [["Element", "Severity", "Kind", "Action"]]
            + [
                [d.name, d.severity.value, d.kind, d.recommended_action]
                for d in report.discrepancies
            ]
            or [["—", "—", "—", "No discrepancies above watch threshold."]],
        ),
    ]
    path = write_report(
        filename=f"drone-progress-{slug}-{report.flight_date.isoformat()}.pdf",
        title=f"Drone Progress Report — {report.project_name}",
        kicker=f"Flight {report.flight_date.isoformat()}  ·  Report {report.report_id}  ·  Human gate required",
        sections=sections,
    )
    return str(path)
