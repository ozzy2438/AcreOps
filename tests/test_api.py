from fastapi.testclient import TestClient

from acreops.api.main import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_catalogs():
    assert len(client.get("/catalog/parcels").json()) >= 3
    assert len(client.get("/catalog/vendors").json()) >= 6
    assert len(client.get("/catalog/tenants").json()) >= 5


def test_triage_webhook():
    res = client.post(
        "/webhooks/appfolio",
        json={
            "tenant_name": "Sam",
            "tenant_phone": "+15125550999",
            "unit_id": "1A",
            "property_id": "harbor-lofts",
            "address": "88 Harbor Way",
            "description": "no heat and it is freezing",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["result"]["classification"]["severity"] == "emergency"
    assert body["result"]["classification"]["trade"] == "hvac"
