from acreops.agents.churn.features import FEATURE_COLUMNS, feature_frame
from acreops.agents.churn.graph import load_leases, run_churn_sweep
from acreops.agents.churn.offers import primary_driver
from acreops.agents.churn.train import train_churn_model
from acreops.schemas.churn import ChurnDriver


def test_feature_matrix_shape():
    leases = load_leases()
    frame = feature_frame(leases)
    assert list(frame.columns[1:]) == FEATURE_COLUMNS
    assert len(frame) == len(leases)


def test_maintenance_driver_for_unresolved():
    lease = next(t for t in load_leases() if t.tenant_id == "T-1042")
    driver, _, _ = primary_driver(lease)
    assert driver is ChurnDriver.MAINTENANCE


def test_churn_sweep_flags_high_risk(tmp_path, monkeypatch):
    from acreops import config

    settings = config.get_settings()
    model_path = tmp_path / "churn.txt"
    monkeypatch.setattr(settings, "churn_model_path", model_path)
    train_churn_model(model_path, n=400)
    run = run_churn_sweep(horizon_days=365, min_probability=0.2, send_email=True)
    assert run.status == "completed"
    assert run.result["predictions"]
    top = run.result["predictions"][0]
    assert 0 <= top["churn_probability"] <= 1
    assert run.result["offers"]
    assert run.result["emails"][0]["status"] in {"demo_queued", "sent"}
