from acreops.agents.drone.graph import run_drone_progress
from acreops.agents.drone.vision import estimate_progress, flag_discrepancies, load_bim


def test_vision_flags_delayed_and_occluded():
    _, elements, observations = load_bim("East 6th Lofts")
    estimates = estimate_progress(elements, observations)
    flags = flag_discrepancies(estimates)
    kinds = {f.kind for f in flags}
    assert "behind_schedule" in kinds
    assert "occlusion" in kinds
    delayed = next(e for e in estimates if e.element_id == "L3-WALLS")
    assert delayed.observed_pct < delayed.planned_pct


def test_drone_report_does_not_update_schedule_without_super():
    run = run_drone_progress(project_name="East 6th Lofts", skip_interrupt=True)
    assert run.result["schedule_updated"] is False
    assert run.result["pdf_path"]
    assert run.result["overall_observed_pct"] < 100
