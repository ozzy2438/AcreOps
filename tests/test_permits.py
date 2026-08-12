from acreops.agents.permits.graph import run_permit_pulse
from acreops.agents.permits.portal import _LAST_SEEN


def test_permit_pulse_detects_forced_change():
    _LAST_SEEN.clear()
    first = run_permit_pulse(force_change=True)
    assert first.status == "completed"
    assert len(first.result["changes"]) >= 1
    change = first.result["changes"][0]
    assert change["old_status"] != change["new_status"]
    assert change["email_sent"] is True
    assert change["notion_updated"] is True
    assert first.result["notifications"]


def test_second_pass_without_force_is_quiet():
    _LAST_SEEN.clear()
    run_permit_pulse(force_change=True)
    quiet = run_permit_pulse(force_change=False)
    assert quiet.result["changes"] == []
