from qvalidate.client import DeviceClient
from qvalidate.models import DeviceState

def test_memory_allocation_limits(device_client: DeviceClient):
    """
    MEM-003: Verify memory utilization tracking under baseline operating parameters.
    """
    status = device_client.get_status()
    assert status.memory_used_mb <= status.memory_total_mb, "Used memory exceeds total RAM"
    assert status.memory_used_mb > 0, "Memory usage should be positive"

def test_memory_pressure_fault_handling(device_client: DeviceClient):
    """
    MEM-004: Inject memory pressure fault and verify state changes to DEGRADED.
    """
    device_client.inject_fault("MEMORY_PRESSURE", intensity=7850.0)
    status = device_client.get_status()
    assert status.state == DeviceState.DEGRADED, f"Expected DEGRADED during pressure, got {status.state}"
    assert status.active_fault == "MEMORY_PRESSURE", "Fault signature missing from telemetry"

    # Recovery check
    device_client.clear_fault()
    status_cleared = device_client.get_status()
    assert status_cleared.state == DeviceState.READY, "State must recover to READY after fault clear"
