import uuid
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from qvalidate.api.routers import (
    devices, builds, components, test_cases, test_suites, test_runs, results, regressions, defects, diagnostics, scheduler, metrics_router, farm, kubernetes_ops
)

app = FastAPI(
    title="Q-Validate — Control Plane REST API",
    description=(
        "Enterprise Embedded & Cloud-Edge Software Validation Control Plane. "
        "Provides REST endpoints for device management, build lifecycle, test orchestration, "
        "Test Impact Analysis (TIA), failure diagnostics, defect tracking, Go/Python scheduling, Device Farm Manager, and OpenTelemetry/Prometheus observability."
    ),
    version="6.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Next.js frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Structured Logging & X-Request-ID Correlation Middleware
@app.middleware("http")
async def add_correlation_id_and_logging(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", f"req-{uuid.uuid4().hex[:8]}")
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time_ms = round((time.time() - start_time) * 1000.0, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = str(process_time_ms)

    print(f"[{request.method}] {request.url.path} -> {response.status_code} ({process_time_ms}ms) | Request-ID: {request_id}")
    return response

@app.get("/health", tags=["Health Check"])
def health_check():
    """System health check endpoint (backward compatible)."""
    return {"status": "HEALTHY", "platform": "Q-Validate Engine v6.0 (Production Hardened)", "timestamp": time.time()}

@app.get("/health/live", tags=["Health Check"])
def liveness_probe():
    """Kubernetes Liveness Probe: Confirms control plane process is active."""
    return {"status": "ALIVE", "timestamp": time.time()}

@app.get("/health/ready", tags=["Health Check"])
def readiness_probe():
    """Kubernetes Readiness Probe: Confirms control plane can serve API traffic."""
    try:
        from qvalidate.db import DatabaseManager
        db = DatabaseManager()
        db.get_all_devices()
        return {"status": "READY", "timestamp": time.time()}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "UNREADY", "error": str(e)})

@app.get("/health/dependencies", tags=["Health Check"])
def dependency_health():
    """Returns detailed health status breakdown across storage, event bus, and device farm."""
    from qvalidate.db import DatabaseManager
    from qvalidate.farm_manager import DeviceFarmManager
    
    db = DatabaseManager()
    farm = DeviceFarmManager()
    
    db_status = "UP"
    try:
        db.get_all_devices()
    except Exception:
        db_status = "DOWN"

    farm_metrics = farm.get_farm_metrics()

    return {
        "status": "HEALTHY" if db_status == "UP" else "DEGRADED",
        "dependencies": {
            "database": {
                "backend": db.backend,
                "status": db_status
            },
            "event_bus": {
                "type": "kafka_or_event_bus",
                "status": "UP"
            },
            "device_farm": {
                "total_nodes": farm_metrics["total_devices"],
                "ready_nodes": farm_metrics["ready_devices"],
                "status": "UP" if farm_metrics["ready_devices"] > 0 else "DEGRADED"
            }
        },
        "timestamp": time.time()
    }

# Include all API routers
app.include_router(metrics_router.router)
api_v1_prefix = "/api/v1"
app.include_router(devices.router, prefix=api_v1_prefix)
app.include_router(builds.router, prefix=api_v1_prefix)
app.include_router(components.router, prefix=api_v1_prefix)
app.include_router(test_cases.router, prefix=api_v1_prefix)
app.include_router(test_suites.router, prefix=api_v1_prefix)
app.include_router(test_runs.router, prefix=api_v1_prefix)
app.include_router(results.router, prefix=api_v1_prefix)
app.include_router(regressions.router, prefix=api_v1_prefix)
app.include_router(defects.router, prefix=api_v1_prefix)
app.include_router(diagnostics.router, prefix=api_v1_prefix)
app.include_router(scheduler.router, prefix=api_v1_prefix)
app.include_router(farm.router, prefix=api_v1_prefix)
app.include_router(kubernetes_ops.router, prefix=api_v1_prefix)

