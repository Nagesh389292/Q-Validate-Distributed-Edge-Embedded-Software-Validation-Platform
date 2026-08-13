from qvalidate.client import DeviceClient
from qvalidate.models import DeviceState

def test_cpu_baseline_telemetry(device_client: DeviceClient):
    """
    CPU-006: Check baseline CPU usage metrics.
    """
    status = device_client.get_status()
    assert 0.0 <= status.cpu_usage_pct <= 100.0, "CPU percentage out of bounds"
    assert status.temperature_celsius < 75.0, f"Baseline temp too high: {status.temperature_celsius}C"

def test_cpu_overload_stress(device_client: DeviceClient):
    """
    CPU-007: Inject CPU overload stress fault and verify thermal escalation.
    """
    device_client.inject_fault("CPU_OVERLOAD", intensity=99.0)
    status = device_client.get_status()
    assert status.cpu_usage_pct >= 85.0, f"CPU load did not scale up: {status.cpu_usage_pct}%"
    assert status.temperature_celsius >= 75.0, f"Thermal escalation missing: {status.temperature_celsius}C"
    assert status.state == DeviceState.DEGRADED, "Device should degrade state during overload"

    device_client.clear_fault()
