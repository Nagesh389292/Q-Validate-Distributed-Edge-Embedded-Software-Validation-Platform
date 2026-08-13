from fastapi import APIRouter, Response
from qvalidate.metrics import PrometheusMetricsRegistry
from qvalidate.tracing import Tracer

router = APIRouter(tags=["Observability & Metrics"])

@router.get("/metrics")
def get_prometheus_metrics():
    """Prometheus metrics exposition endpoint for metric scraping."""
    content = PrometheusMetricsRegistry.generate_prometheus_text()
    return Response(content=content, media_type="text/plain; version=0.0.4; charset=utf-8")

@router.get("/api/v1/observability/traces")
def get_opentelemetry_traces():
    """Retrieve OpenTelemetry distributed traces across services."""
    tracer = Tracer()
    return {"total_spans": len(tracer.get_traces()), "spans": tracer.get_traces(50)}
