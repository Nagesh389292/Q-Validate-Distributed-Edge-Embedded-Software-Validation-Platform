from fastapi.testclient import TestClient
from qvalidate.api.main import app

client = TestClient(app)

def test_trigger_and_cancel_test_run():
    payload = {
        "build_id": "BUILD-1042",
        "device_id": "DEVICE-001",
        "suite_id": "SUITE-SANITY"
    }
    res_trigger = client.post("/api/v1/test-runs", json=payload)
    assert res_trigger.status_code in (200, 202)
    data = res_trigger.json()
    assert data["build_id"] == "BUILD-1042"
    assert data["status"] in ("PASSED", "FAILED", "QUEUED", "RUNNING")
    assert len(data["results"]) == 5

    # Test Cancel
    res_cancel = client.post(f"/api/v1/test-runs/{data['run_id']}/cancel")
    assert res_cancel.status_code == 200
    assert res_cancel.json()["success"] is True
