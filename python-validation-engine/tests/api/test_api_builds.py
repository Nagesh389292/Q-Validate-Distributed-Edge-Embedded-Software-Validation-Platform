import uuid
from fastapi.testclient import TestClient
from qvalidate.api.main import app

client = TestClient(app)

def test_build_lifecycle_api():
    unique_build_id = f"BUILD-API-{uuid.uuid4().hex[:6].upper()}"
    build_data = {
        "build_id": unique_build_id,
        "version": "4.3.0-rc1",
        "git_commit": "c0mm1t990011",
        "branch": "release/4.3"
    }
    res_create = client.post("/api/v1/builds", json=build_data)
    assert res_create.status_code == 201
    assert res_create.json()["build_id"] == unique_build_id
    assert res_create.json()["status"] == "CREATED"

    res_list = client.get("/api/v1/builds")
    assert res_list.status_code == 200
    ids = [b["build_id"] for b in res_list.json()]
    assert unique_build_id in ids

    res_get = client.get(f"/api/v1/builds/{unique_build_id}")
    assert res_get.status_code == 200
    assert res_get.json()["version"] == "4.3.0-rc1"
