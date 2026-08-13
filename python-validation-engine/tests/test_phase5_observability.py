import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qvalidate.tracing import Tracer
from qvalidate.metrics import PrometheusMetricsRegistry
from qvalidate.logging_config import get_structured_logger

def test_opentelemetry_tracer():
    tracer = Tracer()
    span = tracer.start_span(name="test_execution_span", trace_id="trace-100200")
    span.set_attribute("test_id", "MEM-003")
    span.add_event("DEVICE_RESERVED", {"device_id": "DEVICE-002"})
    span.finish()

    traces = tracer.get_traces()
    assert len(traces) > 0
    last_span = traces[-1]
    assert last_span["name"] == "test_execution_span"
    assert last_span["trace_id"] == "trace-100200"
    assert last_span["attributes"]["test_id"] == "MEM-003"
    assert last_span["duration_ms"] >= 0.0

def test_prometheus_metrics_registry():
    registry = PrometheusMetricsRegistry()
    registry.record_test_run(status="PASS", duration_sec=0.25)
    registry.record_fault_injection(fault_type="CPU_OVERLOAD")
    registry.update_queue_metrics(depth=3, active_workers=10)

    text_output = PrometheusMetricsRegistry.generate_prometheus_text()

    assert "qvalidate_test_runs_total" in text_output
    assert "qvalidate_scheduler_queue_depth 3" in text_output
    assert "qvalidate_worker_utilization 10" in text_output
    assert "qvalidate_device_faults_total" in text_output

def test_structured_json_logger():
    logger = get_structured_logger("qvalidate.test")
    assert logger is not None
