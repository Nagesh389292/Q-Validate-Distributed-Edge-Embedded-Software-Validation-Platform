import pytest
from qvalidate.farm_manager import DeviceFarmManager, DeviceState

def test_device_health_scoring():
    farm = DeviceFarmManager()
    farm.scale_farm(10)
    
    profile = farm.farm["DEVICE-001"]
    assert profile.health_score == 100.0
    
    # Record 3 failures
    profile.record_test_result(passed=False, latency_ms=45.0)
    profile.record_test_result(passed=False, latency_ms=50.0)
    profile.record_test_result(passed=False, latency_ms=55.0)
    
    assert profile.health_score < 70.0
    assert profile.test_failures_count == 3

def test_degraded_isolation():
    farm = DeviceFarmManager()
    farm.scale_farm(10)
    
    profile = farm.farm["DEVICE-002"]
    # Record 5 failures to drop health score below 50
    for _ in range(5):
        profile.record_test_result(passed=False, latency_ms=60.0)
    
    assert profile.health_score < 50.0
    assert profile.status == DeviceState.DEGRADED
    
    # Recover
    farm.recover_degraded_device("DEVICE-002")
    assert profile.status == DeviceState.READY
    assert profile.health_score == 100.0
