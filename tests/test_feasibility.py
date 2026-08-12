from acreops.agents.feasibility.graph import run_feasibility
from acreops.agents.feasibility.research import compile_zoning
from acreops.schemas.feasibility import FeasibilityRequest


def test_zoning_catalog_hit():
    req = FeasibilityRequest(
        address="1408 East 6th Street",
        city="Austin",
        state="TX",
        zip_code="78702",
        intended_use="multifamily",
    )
    zoning = compile_zoning(req)
    assert zoning.zone_code.startswith("CS-MU")
    assert zoning.opportunity_zone is True


def test_feasibility_packet_end_to_end(tmp_path, monkeypatch):
    from acreops import config

    settings = config.get_settings()
    monkeypatch.setattr(settings, "acreops_artifact_dir", tmp_path)
    run = run_feasibility(
        {
            "address": "1408 East 6th Street",
            "city": "Austin",
            "state": "TX",
            "zip_code": "78702",
            "intended_use": "multifamily",
            "land_price_usd": 4_500_000,
            "signer_name": "Jordan Hale",
            "signer_email": "jordan@example.com",
        }
    )
    assert run.status == "completed"
    assert run.result["ready_to_sign"] is True
    assert run.result["pandadoc_document_id"]
    assert run.result["pdf_path"]
    assert len(run.result["scenarios"]) == 3
    assert run.result["zoning"]["jurisdiction"] == "City of Austin"
