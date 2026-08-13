import time
from qvalidate.client import DeviceClient

def test_telemetry_collection_performance(device_client: DeviceClient):
    """
    PERF-021: Verify high-frequency telemetry sampling performance (< 50ms per batch).
    """
    start = time.time()
    samples = device_client.collect_metrics(count=10)
    dur_ms = (time.time() - start) * 1000.0
    assert len(samples) == 10, "Expected 10 metric samples"
    assert dur_ms < 50.0, f"Sampling latency exceeded threshold: {dur_ms:.2f}ms"
