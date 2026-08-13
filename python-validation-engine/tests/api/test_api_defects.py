from fastapi.testclient import TestClient
from qvalidate.api.main import app

client = TestClient(app)

def test_defects_and_triage_api():
    # 1. Trigger diagnostic triage on a test run
    res_run = client.post("/api/v1/test-runs", json={"build_id": "BUILD-1042", "device_id": "DEVICE-001", "suite_id": "SUITE-SANITY"})
    run_id = res_run.json()["run_id"]

    res_triage = client.post(f"/api/v1/diagnostics/triage/{run_id}")
    assert res_triage.status_code == 200

    # 2. Get list of defects
    res_defects = client.get("/api/v1/defects")
    assert res_defects.status_code == 200
    defects = res_defects.json()
    assert isinstance(defects, list)

    if len(defects) > 0:
        defect_id = defects[0]["defect_id"]
        # Update defect status
        res_patch = client.patch(f"/api/v1/defects/{defect_id}", json={"status": "TRIAGED", "root_cause": "Root cause verified via API test"})
        assert res_patch.status_code == 200
        assert res_patch.json()["status"] == "TRIAGED"
