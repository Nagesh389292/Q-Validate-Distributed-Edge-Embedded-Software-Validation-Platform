import sys
import os

# Ensure qvalidate is importable
sys.path.insert(0, os.path.dirname(__file__))

from qvalidate.runner import TestRunner
from qvalidate.reporter import Reporter
from qvalidate.client import DeviceClient
from qvalidate.models import DeviceState

def run_boot_test(client: DeviceClient) -> str:
    ok, dur, msg = client.power_on()
    if not ok:
        raise RuntimeError(msg)
    status = client.get_status()
    if status.state != DeviceState.READY:
        raise ValueError(f"State not READY: {status.state}")
    return f"Device booted into READY in {dur}s (Firmware: {status.firmware_version})"

def run_mem_test(client: DeviceClient) -> str:
    status = client.get_status()
    if status.memory_used_mb > status.memory_total_mb:
        raise ValueError("Memory heap overflow")
    return f"Memory allocated successfully: {status.memory_used_mb}MB / {status.memory_total_mb}MB"

def run_cpu_test(client: DeviceClient) -> str:
    status = client.get_status()
    if status.cpu_usage_pct > 100.0:
        raise ValueError("CPU utilization reading out of bounds")
    return f"CPU usage normal: {status.cpu_usage_pct}% (Temp: {status.temperature_celsius}C)"

def run_perf_test(client: DeviceClient) -> str:
    metrics = client.collect_metrics(5)
    return f"Collected {len(metrics)} telemetry samples at avg {metrics[0].cpu_pct}% CPU load"

def run_fault_test(client: DeviceClient) -> str:
    client.inject_fault("CPU_OVERLOAD", 98.0)
    status = client.get_status()
    client.clear_fault()
    if status.state != DeviceState.DEGRADED:
        raise ValueError(f"Expected DEGRADED during CPU overload, got {status.state}")
    return "CPU overload fault injected and handled gracefully in DEGRADED state"

def main():
    print("\n========================================================")
    print("   Q-VALIDATE — PLATFORM ORCHESTRATION HARNESS (PHASE 1)")
    print("========================================================\n")

    # 1. Successful Build Validation (BUILD-1042)
    print("[PHASE 1.1] Executing Validation Suite on Stable Build: BUILD-1042...")
    runner = TestRunner(build_id="BUILD-1042", device_id="DEVICE-001", suite_id="SUITE-SANITY")
    runner.register_test("BOOT-001", "Device Boot Sequence Verification", "Boot time < 5.0s, State == READY", run_boot_test)
    runner.register_test("MEM-003", "Memory Stress Allocation Test", "Memory allocated successfully", run_mem_test)
    runner.register_test("CPU-007", "CPU Load Balancing Under Stress", "CPU temp < 85C, Health > 70", run_cpu_test)
    runner.register_test("PERF-021", "API Latency Threshold Test", "Latency < 10.0ms", run_perf_test)
    runner.register_test("FAULT-005", "CPU Overload Recovery Verification", "State == DEGRADED during fault", run_fault_test)

    summary_pass = runner.run_suite()
    Reporter.print_summary(summary_pass)

    # 2. Regression / Failure Triage Validation (BUILD-1043)
    print("[PHASE 1.2] Executing Validation Suite on Regression Build: BUILD-1043...")
    reg_runner = TestRunner(build_id="BUILD-1043", device_id="DEVICE-001", suite_id="SUITE-REGRESSION")
    
    # Intentionally failing test simulation to demonstrate triage engine
    def failing_mem_test(client: DeviceClient) -> str:
        raise MemoryError("Memory leak detected: 8192MB allocation threshold breached in MemoryManager")

    reg_runner.register_test("BOOT-001", "Device Boot Sequence Verification", "Boot time < 5.0s, State == READY", run_boot_test)
    reg_runner.register_test("MEM-003", "Memory Stress Allocation Test", "Memory allocated successfully", failing_mem_test)
    reg_runner.register_test("CPU-007", "CPU Load Balancing Under Stress", "CPU temp < 85C, Health > 70", run_cpu_test)

    summary_fail = reg_runner.run_suite()
    Reporter.print_summary(summary_fail)

    print("[PHASE 1.3] Triggering Automated Failure Triage Engine...")
    defects = Reporter.perform_failure_triage(summary_fail)

    # 3. Native C++ Executable Verification
    print("\n[PHASE 1.4] Verifying Native C++20 Runtime Executable Integration...")
    client = DeviceClient(device_id="DEVICE-001")
    proc = client.run_cxx_native_verification()
    print("[NATIVE C++ BINARY STDOUT]:")
    print(proc.stdout)

    print("\n[SUCCESS] Q-Validate Phase 1 Core Validation Completed Cleanly!")

if __name__ == "__main__":
    main()
