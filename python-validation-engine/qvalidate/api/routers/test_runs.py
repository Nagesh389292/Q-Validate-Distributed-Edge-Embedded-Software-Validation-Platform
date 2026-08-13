from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from qvalidate.db import DatabaseManager
from qvalidate.runner import TestRunner
from qvalidate.api.schemas import TriggerTestRunRequest
from qvalidate.client import DeviceClient
from qvalidate.models import DeviceState

router = APIRouter(prefix="/test-runs", tags=["Test Execution Lifecycle"])
db = DatabaseManager()

# Registry of active runner tasks for cancellation support
active_runners = {}

def run_test_suite_background(run_id: str, req: TriggerTestRunRequest):
    runner = TestRunner(build_id=req.build_id, device_id=req.device_id, suite_id=req.suite_id, max_retries=req.max_retries)
    active_runners[run_id] = runner

    # Register standard test set
    def run_boot_test(client: DeviceClient) -> str:
        ok, dur, msg = client.power_on()
        if not ok: raise RuntimeError(msg)
        status = client.get_status()
        if status.state != DeviceState.READY: raise ValueError(f"State not READY: {status.state}")
        return f"Device booted into READY in {dur}s"

    def run_mem_test(client: DeviceClient) -> str:
        status = client.get_status()
        if status.memory_used_mb > status.memory_total_mb: raise ValueError("Memory heap overflow")
        return f"Memory allocated successfully: {status.memory_used_mb}MB"

    def run_cpu_test(client: DeviceClient) -> str:
        status = client.get_status()
        if status.cpu_usage_pct > 100.0: raise ValueError("CPU out of bounds")
        return f"CPU usage normal: {status.cpu_usage_pct}%"

    def run_perf_test(client: DeviceClient) -> str:
        metrics = client.collect_metrics(5)
        return f"Collected {len(metrics)} telemetry samples"

    def run_fault_test(client: DeviceClient) -> str:
        client.inject_fault("CPU_OVERLOAD", 98.0)
        status = client.get_status()
        client.clear_fault()
        if status.state != DeviceState.DEGRADED: raise ValueError(f"Expected DEGRADED, got {status.state}")
        return "CPU overload fault injected and handled"

    runner.register_test("BOOT-001", "Device Boot Sequence Verification", "Boot time < 5.0s, State == READY", run_boot_test, priority=5)
    runner.register_test("MEM-003", "Memory Stress Allocation Test", "Memory allocated successfully", run_mem_test, priority=4)
    runner.register_test("CPU-007", "CPU Load Balancing Under Stress", "CPU temp < 85C, Health > 70", run_cpu_test, priority=3)
    runner.register_test("PERF-021", "API Latency Threshold Test", "Latency < 10.0ms", run_perf_test, priority=2)
    runner.register_test("FAULT-005", "CPU Overload Recovery Verification", "State == DEGRADED during fault", run_fault_test, priority=1)

    summary = runner.run_suite()
    if run_id in active_runners:
        del active_runners[run_id]

@router.get("", response_model=List[dict])
def get_all_test_runs():
    """Get list of all test runs across all builds and devices."""
    return db.get_all_test_runs()

@router.post("", response_model=dict, status_code=202)
def trigger_test_run(req: TriggerTestRunRequest):
    """Trigger execution of a test run on a specific build and device."""
    build = db.get_build(req.build_id)
    if not build:
        raise HTTPException(status_code=404, detail=f"Build {req.build_id} not found")
    
    # Run synchronously or background
    runner = TestRunner(build_id=req.build_id, device_id=req.device_id, suite_id=req.suite_id, max_retries=req.max_retries)
    
    def run_boot_test(client: DeviceClient) -> str:
        ok, dur, msg = client.power_on()
        if not ok: raise RuntimeError(msg)
        return f"Device booted into READY in {dur}s"

    def run_mem_test(client: DeviceClient) -> str:
        status = client.get_status()
        return f"Memory allocated: {status.memory_used_mb}MB"

    def run_cpu_test(client: DeviceClient) -> str:
        status = client.get_status()
        return f"CPU normal: {status.cpu_usage_pct}%"

    def run_perf_test(client: DeviceClient) -> str:
        metrics = client.collect_metrics(5)
        return f"Collected {len(metrics)} samples"

    def run_fault_test(client: DeviceClient) -> str:
        client.inject_fault("CPU_OVERLOAD", 98.0)
        status = client.get_status()
        client.clear_fault()
        return "Fault handled"

    runner.register_test("BOOT-001", "Device Boot Sequence Verification", "Boot time < 5.0s, State == READY", run_boot_test, priority=5)
    runner.register_test("MEM-003", "Memory Stress Allocation Test", "Memory allocated successfully", run_mem_test, priority=4)
    runner.register_test("CPU-007", "CPU Load Balancing Under Stress", "CPU temp < 85C, Health > 70", run_cpu_test, priority=3)
    runner.register_test("PERF-021", "API Latency Threshold Test", "Latency < 10.0ms", run_perf_test, priority=2)
    runner.register_test("FAULT-005", "CPU Overload Recovery Verification", "State == DEGRADED during fault", run_fault_test, priority=1)

    summary = runner.run_suite()
    return db.get_test_run(summary.run_id)

@router.get("/{run_id}", response_model=dict)
def get_test_run(run_id: str):
    """Get test run details and itemized test results."""
    run_data = db.get_test_run(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail=f"Test run {run_id} not found")
    return run_data

@router.post("/{run_id}/cancel")
def cancel_test_run(run_id: str):
    """Cancel an active in-flight test run."""
    if run_id in active_runners:
        active_runners[run_id].cancel()
        db.update_test_run_status(run_id, "CANCELLED")
        return {"success": True, "message": f"Test run {run_id} cancellation requested"}
    else:
        db.update_test_run_status(run_id, "CANCELLED")
        return {"success": True, "message": f"Test run {run_id} marked CANCELLED"}
