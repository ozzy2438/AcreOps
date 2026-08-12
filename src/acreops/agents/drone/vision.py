from __future__ import annotations

from acreops.adapters.catalog import bim_models
from acreops.schemas.drone import (
    BimElement,
    Discrepancy,
    DiscrepancySeverity,
    ElementStatus,
    ProgressEstimate,
)


def load_bim(project_name: str | None = None) -> tuple[str, list[BimElement], list[dict]]:
    models = bim_models()
    model = next((m for m in models if m["project_name"] == project_name), models[0])
    elements = [BimElement.model_validate(el) for el in model["elements"]]
    return model["project_name"], elements, model.get("observations", [])


def estimate_progress(elements: list[BimElement], observations: list[dict]) -> list[ProgressEstimate]:
    obs_by_id = {o["element_id"]: o for o in observations}
    estimates: list[ProgressEstimate] = []
    for el in elements:
        obs = obs_by_id.get(el.element_id, {})
        observed = float(obs.get("observed_pct", max(el.planned_pct - 8, 0)))
        occlusion = bool(obs.get("occlusion", False))
        delta = observed - el.planned_pct
        if occlusion:
            status = ElementStatus.OCCLUDED
        elif observed >= 99:
            status = ElementStatus.COMPLETE
        elif delta <= -12:
            status = ElementStatus.DELAYED
        elif delta >= 10:
            status = ElementStatus.AHEAD
        elif observed <= 2:
            status = ElementStatus.NOT_STARTED
        else:
            status = ElementStatus.IN_PROGRESS
        estimates.append(
            ProgressEstimate(
                element_id=el.element_id,
                name=el.name,
                planned_pct=el.planned_pct,
                observed_pct=round(observed, 1),
                delta_pct=round(delta, 1),
                status=status,
                confidence=0.62 if occlusion else float(obs.get("confidence", 0.84)),
                evidence=obs.get(
                    "evidence",
                    "Orthomosaic vs. BIM envelope: volume occupancy heuristic (demo vision).",
                ),
                occlusion=occlusion,
            )
        )
    return estimates


def flag_discrepancies(estimates: list[ProgressEstimate]) -> list[Discrepancy]:
    flags: list[Discrepancy] = []
    for est in estimates:
        if est.occlusion:
            flags.append(
                Discrepancy(
                    element_id=est.element_id,
                    name=est.name,
                    severity=DiscrepancySeverity.WATCH,
                    kind="occlusion",
                    description="Drone view is occluded (staging, weather, or canopy). Do not update the schedule from this observation.",
                    recommended_action="Re-fly this grid or walk the element before changing dates.",
                )
            )
        elif est.delta_pct <= -15:
            flags.append(
                Discrepancy(
                    element_id=est.element_id,
                    name=est.name,
                    severity=DiscrepancySeverity.CRITICAL
                    if est.delta_pct <= -25
                    else DiscrepancySeverity.MATERIAL,
                    kind="behind_schedule",
                    description=(
                        f"Observed {est.observed_pct:.0f}% vs planned {est.planned_pct:.0f}% "
                        f"({est.delta_pct:.0f} pp)."
                    ),
                    recommended_action="Superintendent to confirm crew / material constraint before slipping the look-ahead.",
                )
            )
        elif est.delta_pct >= 12:
            flags.append(
                Discrepancy(
                    element_id=est.element_id,
                    name=est.name,
                    severity=DiscrepancySeverity.INFO,
                    kind="ahead_of_schedule",
                    description=f"Observed {est.observed_pct:.0f}% vs planned {est.planned_pct:.0f}%.",
                    recommended_action="Confirm quality hold-points before pulling successor activities forward.",
                    requires_superintendent=True,
                )
            )
        elif abs(est.delta_pct) >= 8:
            flags.append(
                Discrepancy(
                    element_id=est.element_id,
                    name=est.name,
                    severity=DiscrepancySeverity.WATCH,
                    kind="geometry_mismatch",
                    description="Volume occupancy disagrees with the 4D BIM planned envelope.",
                    recommended_action="Spot-check against last week's point cloud before logging a delay.",
                )
            )
    return flags


def schedule_delta_days(estimates: list[ProgressEstimate]) -> float:
    if not estimates:
        return 0.0
    # Rough: 1 percentage point of average lag ≈ 0.12 days on a mid-rise pour cycle.
    avg = sum(e.delta_pct for e in estimates) / len(estimates)
    return round(avg * 0.12, 1)
