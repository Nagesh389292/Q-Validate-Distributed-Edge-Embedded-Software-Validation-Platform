import pytest
from fastapi.testclient import TestClient
from qvalidate.api.main import app

client = TestClient(app)

def test_get_all_devices():
    res = client.get("/api/v1/devices")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[0]["device_id"] == "DEVICE-001"

def test_device_power_on():
    res = client.post("/api/v1/devices/DEVICE-001/power-on")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["state"] == "READY"

def test_device_fault_injection_and_clear():
    # Inject Fault
    res_inject = client.post("/api/v1/devices/DEVICE-001/inject-fault", json={"fault_type": "CPU_OVERLOAD", "intensity": 98.5})
    assert res_inject.status_code == 200
    assert res_inject.json()["state"] == "DEGRADED"

    # Clear Fault
    res_clear = client.post("/api/v1/devices/DEVICE-001/clear-fault")
    assert res_clear.status_code == 200
    assert res_clear.json()["state"] == "READY"
