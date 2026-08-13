from fastapi import APIRouter, Query, HTTPException
from qvalidate.farm_manager import DeviceFarmManager
from qvalidate.capacity_planner import CapacityPlanner

router = APIRouter(prefix="/farm", tags=["Device Farm Manager"])
farm_manager = DeviceFarmManager()
capacity_planner = CapacityPlanner(farm_manager=farm_manager)

@router.get("/devices", response_model=dict)
def get_farm_devices():
    """Retrieve all simulated device profiles and lifecycle states."""
    profiles = farm_manager.get_all_device_profiles()
    return {"total": len(profiles), "devices": profiles}

@router.get("/metrics", response_model=dict)
def get_farm_metrics():
    """Retrieve device farm utilization, node counts, and state breakdown."""
    return farm_manager.get_farm_metrics()

@router.post("/scale", response_model=dict)
def scale_farm(node_count: int = Query(25, ge=5, le=100)):
    """Scale device farm node count up to 25, 50, or 100 simulated edge nodes."""
    scaled_count = farm_manager.scale_farm(target_nodes=node_count)
    return {"message": f"Device farm scaled to {scaled_count} nodes", "node_count": scaled_count}

@router.post("/recover/{device_id}", response_model=dict)
def recover_device(device_id: str):
    """Trigger hardware self-test recovery workflow for a degraded device node."""
    success = farm_manager.recover_degraded_device(device_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found in farm")
    return {"message": f"Device {device_id} successfully recovered into READY state", "status": "READY"}

@router.get("/capacity", response_model=dict)
def get_capacity_planning(test_count: int = Query(100, ge=1)):
    """Calculate capacity planning workload completion estimations."""
    return capacity_planner.estimate_completion_time(test_count=test_count)
