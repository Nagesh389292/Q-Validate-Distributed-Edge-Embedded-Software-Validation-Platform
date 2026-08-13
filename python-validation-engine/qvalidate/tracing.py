import time
import uuid
from typing import Dict, List, Optional
from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider, Span as OtelSpan
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import Status, StatusCode

# Initialize Official OpenTelemetry SDK Provider & In-Memory / OTLP Exporter
_provider = TracerProvider()
_exporter = InMemorySpanExporter()
_processor = SimpleSpanProcessor(_exporter)
_provider.add_span_processor(_processor)
otel_trace.set_tracer_provider(_provider)
_otel_tracer = otel_trace.get_tracer("qvalidate-control-plane", "5.0.0")

class Span:
    def __init__(self, name: str, trace_id: str, parent_span_id: Optional[str] = None, service_name: str = "qvalidate-control-plane"):
        self.name = name
        self.trace_id = trace_id
        self.span_id = f"span-{uuid.uuid4().hex[:8]}"
        self.parent_span_id = parent_span_id
        self.service_name = service_name
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.attributes: Dict[str, str] = {"service.name": service_name}
        self.events: List[Dict] = []
        self.status: str = "OK"

        # Official OpenTelemetry SDK Span Instance
        self._otel_span: OtelSpan = _otel_tracer.start_span(name)
        self._otel_span.set_attribute("service.name", service_name)
        self._otel_span.set_attribute("qvalidate.trace_id", trace_id)
        if parent_span_id:
            self._otel_span.set_attribute("qvalidate.parent_span_id", parent_span_id)

    def set_attribute(self, key: str, value: str):
        self.attributes[key] = str(value)
        self._otel_span.set_attribute(key, str(value))

    def add_event(self, event_name: str, payload: Optional[Dict] = None):
        self.events.append({
            "name": event_name,
            "timestamp": time.time(),
            "payload": payload or {}
        })
        self._otel_span.add_event(event_name, attributes={k: str(v) for k, v in (payload or {}).items()})

    def set_status_error(self, error_message: str):
        self.status = "ERROR"
        self.set_attribute("error", "true")
        self.set_attribute("error.message", error_message)
        self._otel_span.set_status(Status(StatusCode.ERROR, error_message))

    def finish(self):
        self.end_time = time.time()
        self._otel_span.end()
        Tracer().record_span(self)

class Tracer:
    """
    Official OpenTelemetry SDK-backed Distributed Tracer for Q-Validate.
    Wraps opentelemetry.sdk.trace.TracerProvider and OTLP/InMemory exporters.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Tracer, cls).__new__(cls)
            cls._instance.completed_spans = []
        return cls._instance

    def start_span(self, name: str, trace_id: Optional[str] = None, parent_span_id: Optional[str] = None, service_name: str = "qvalidate-control-plane") -> Span:
        if not trace_id:
            trace_id = f"trace-{uuid.uuid4().hex[:12]}"
        return Span(name=name, trace_id=trace_id, parent_span_id=parent_span_id, service_name=service_name)

    def record_span(self, span: Span):
        duration_ms = round(((span.end_time or time.time()) - span.start_time) * 1000.0, 2)
        record = {
            "name": span.name,
            "service_name": span.service_name,
            "trace_id": span.trace_id,
            "span_id": span.span_id,
            "parent_span_id": span.parent_span_id,
            "duration_ms": duration_ms,
            "status": span.status,
            "attributes": span.attributes,
            "events": span.events,
            "timestamp": span.start_time,
            "otel_instrumented": True
        }
        self.completed_spans.append(record)

    def get_traces_by_trace_id(self, trace_id: str) -> List[Dict]:
        return [s for s in self.completed_spans if s["trace_id"] == trace_id]

    def get_traces(self, limit: int = 50) -> List[Dict]:
        return self.completed_spans[-limit:]

    def get_raw_otel_spans(self):
        """Returns official OpenTelemetry SDK span data exported via InMemorySpanExporter."""
        return _exporter.get_finished_spans()
