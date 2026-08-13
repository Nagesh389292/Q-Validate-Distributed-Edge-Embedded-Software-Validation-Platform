import pytest
from fastapi.testclient import TestClient
from qvalidate.api.main import app
from qvalidate.distributed_runner import DistributedTestWorkerPool

client = TestClient(app)

def test_liveness_probe():
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ALIVE"

def test_readiness_probe():
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "READY"

def test_dependency_health():
    response = client.get("/health/dependencies")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("HEALTHY", "DEGRADED")
    assert "database" in data["dependencies"]
    assert "event_bus" in data["dependencies"]
    assert "device_farm" in data["dependencies"]

def test_task_idempotency_guard():
    pool = DistributedTestWorkerPool()
    run_id = "RUN-IDEM-001"
    test_id = "BOOT-001"
    
    # First invocation -> New task
    is_new_1 = pool.process_task_idempotent(run_id, test_id)
    assert is_new_1 is True
    
    # Second duplicate invocation -> Duplicate ignored
    is_new_2 = pool.process_task_idempotent(run_id, test_id)
    assert is_new_2 is False

def test_graceful_shutdown_flag():
    pool = DistributedTestWorkerPool()
    assert pool.is_shutting_down is False
    pool.is_shutting_down = True
    assert pool.is_shutting_down is True
