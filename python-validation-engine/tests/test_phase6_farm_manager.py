import pytest
from qvalidate.farm_manager import DeviceFarmManager, DeviceState
from qvalidate.capacity_planner import CapacityPlanner

def test_farm_manager_init():
    farm = DeviceFarmManager()
    farm.scale_farm(25)
    metrics = farm.get_farm_metrics()
    assert metrics["total_devices"] == 25
    assert metrics["ready_devices"] == 25
    assert metrics["error_devices"] == 0

def test_farm_manager_state_transition():
    farm = DeviceFarmManager()
    farm.scale_farm(25)
    
    assert farm.transition_state("DEVICE-001", DeviceState.TESTING) is True
    metrics = farm.get_farm_metrics()
    assert metrics["allocated_devices"] == 1

def test_farm_manager_recovery():
    farm = DeviceFarmManager()
    farm.scale_farm(25)
    farm.transition_state("DEVICE-005", DeviceState.ERROR)
    
    assert farm.recover_degraded_device("DEVICE-005") is True
    dev = next(p for p in farm.get_all_device_profiles() if p["device_id"] == "DEVICE-005")
    assert dev["status"] == DeviceState.READY

def test_capacity_planner_calculation():
    farm = DeviceFarmManager()
    farm.scale_farm(50)
    planner = CapacityPlanner(farm_manager=farm)
    
    est = planner.estimate_completion_time(test_count=100, avg_duration_sec=0.05)
    assert est["queued_test_count"] == 100
    assert est["active_ready_nodes"] == 50
    assert est["estimated_completion_seconds"] == 0.1
    assert est["estimated_throughput_tps"] == 1000.0
