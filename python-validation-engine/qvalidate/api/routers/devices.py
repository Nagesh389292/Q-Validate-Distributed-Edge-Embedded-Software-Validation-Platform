from fastapi import APIRouter, HTTPException, Depends
from typing import List
from qvalidate.db import DatabaseManager
from qvalidate.client import DeviceClient
from qvalidate.api.schemas import FaultInjectRequest

router = APIRouter(prefix="/devices", tags=["Device Management"])
db = DatabaseManager()

@router.get("", response_model=List[dict])
def get_all_devices():
    """Retrieve list of all simulated embedded edge devices."""
    return db.get_all_devices()

@router.get("/{device_id}", response_model=dict)
def get_device(device_id: str):
    """Get live telemetry and state for a specific device."""
    dev = db.get_device(device_id)
    if not dev:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    client = DeviceClient(device_id=device_id)
    status = client.get_status()
    dev["cpu_usage_pct"] = status.cpu_usage_pct
    dev["memory_used_mb"] = status.memory_used_mb
    dev["temperature_celsius"] = status.temperature_celsius
    dev["status"] = status.state.value
    return dev

@router.post("/{device_id}/power-on")
def power_on_device(device_id: str):
    """Trigger device power-on sequence."""
    client = DeviceClient(device_id=device_id)
    ok, dur, msg = client.power_on()
    status = client.get_status()
    db.update_device_status(device_id, status.state.value, status.cpu_usage_pct, status.memory_used_mb, status.temperature_celsius)
    return {"success": ok, "duration_sec": dur, "message": msg, "state": status.state.value}

@router.post("/{device_id}/reset")
def reset_device(device_id: str, hard_reset: bool = False):
    """Trigger hard or soft device reset."""
    client = DeviceClient(device_id=device_id)
    ok, dur, msg = client.reset(hard_reset=hard_reset)
    status = client.get_status()
    db.update_device_status(device_id, status.state.value, status.cpu_usage_pct, status.memory_used_mb, status.temperature_celsius)
    return {"success": ok, "duration_sec": dur, "message": msg, "state": status.state.value}

@router.post("/{device_id}/inject-fault")
def inject_fault(device_id: str, req: FaultInjectRequest):
    """Inject hardware/software fault into simulated device runtime."""
    client = DeviceClient(device_id=device_id)
    ok, msg = client.inject_fault(req.fault_type, req.intensity)
    status = client.get_status()
    db.update_device_status(device_id, status.state.value, status.cpu_usage_pct, status.memory_used_mb, status.temperature_celsius)
    return {"success": ok, "message": msg, "state": status.state.value, "active_fault": status.active_fault}

@router.post("/{device_id}/clear-fault")
def clear_fault(device_id: str):
    """Clear all active faults on simulated device."""
    client = DeviceClient(device_id=device_id)
    ok, msg = client.clear_fault()
    status = client.get_status()
    db.update_device_status(device_id, status.state.value, status.cpu_usage_pct, status.memory_used_mb, status.temperature_celsius)
    return {"success": ok, "message": msg, "state": status.state.value}
