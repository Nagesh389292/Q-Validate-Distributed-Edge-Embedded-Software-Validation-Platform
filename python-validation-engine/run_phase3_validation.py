import sys
import os
import time
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(__file__))

from qvalidate.api.main import app
from qvalidate.client import DeviceClient

def main():
    print("\n========================================================")
    print("   Q-VALIDATE — ENGINEERING PORTAL INTEGRATION (PHASE 3)")
    print("========================================================\n")

    client = TestClient(app)

    # 1. API Health Check
    print("[PHASE 3.1] Verifying System Health & API Connectivity...")
    res_health = client.get("/health")
    print(f"  -> Health Endpoint: {res_health.json()}")
    assert res_health.status_code == 200

    # 2. Workflow 1: Device Telemetry & Control
    print("\n[PHASE 3.2] Verifying Workflow 1: Device Control & Fault Injection...")
    res_devices = client.get("/api/v1/devices")
    devices = res_devices.json()
    print(f"  -> Total Devices Registered: {len(devices)}")
    assert len(devices) >= 1

    target_dev = devices[0]["device_id"]
    res_power = client.post(f"/api/v1/devices/{target_dev}/power-on")
    print(f"  -> Power On {target_dev}: {res_power.json()}")
    assert res_power.json()["state"] == "READY"

    res_fault = client.post(f"/api/v1/devices/{target_dev}/inject-fault", json={"fault_type": "CPU_OVERLOAD", "intensity": 99.0})
    print(f"  -> Injected Fault CPU_OVERLOAD: {res_fault.json()}")
    assert res_fault.json()["state"] == "DEGRADED"

    res_clear = client.post(f"/api/v1/devices/{target_dev}/clear-fault")
    print(f"  -> Cleared Fault: {res_clear.json()}")
    assert res_clear.json()["state"] == "READY"

    # 3. Workflow 2: Build Registration & Test Execution
    print("\n[PHASE 3.3] Verifying Workflow 2: Build Registration & Test Execution...")
    res_build = client.post("/api/v1/builds", json={
        "build_id": "BUILD-3001",
        "version": "4.4.0-rc1",
        "git_commit": "3a4b5c6d7e8f",
        "branch": "release/4.4"
    })
    print(f"  -> Registered Build BUILD-3001: {res_build.json()}")
    assert res_build.status_code == 201

    res_run = client.post("/api/v1/test-runs", json={
        "build_id": "BUILD-3001",
        "device_id": target_dev,
        "suite_id": "SUITE-SANITY",
        "max_retries": 1
    })
    run_data = res_run.json()
    print(f"  -> Executed Test Run [{run_data['run_id']}]: Status = {run_data['status']}")
    print(f"     * Total: {run_data['total_tests']} | Passed: {run_data['passed_tests']} | Failed: {run_data['failed_tests']}")
    assert run_data["status"] == "PASSED"

    # 4. Workflow 3: Test Impact Analysis (TIA) Studio
    print("\n[PHASE 3.4] Verifying Workflow 3: Test Impact Analysis (TIA)...")
    res_tia = client.post("/api/v1/regressions/impact-analysis", json={
        "changed_files": ["src/MemoryManager.cpp", "include/Memory.hpp"]
    })
    tia_data = res_tia.json()
    print(f"  -> TIA Changed Files : {tia_data['changed_files']}")
    print(f"  -> Impacted Components: {tia_data['impacted_component_ids']}")
    print(f"  -> Selected Test Count: {tia_data['selected_test_count']}")
    assert "COMP-MEM" in tia_data['impacted_component_ids']
    assert tia_data['selected_test_count'] >= 1

    # 5. C++ Executable Runtime Verification
    print("\n[PHASE 3.5] Verifying Native C++20 Device Executable Runtime...")
    dev_client = DeviceClient(device_id="DEVICE-001")
    proc = dev_client.run_cxx_native_verification()
    print("[NATIVE C++ EXECUTABLE STDOUT]:")
    print(proc.stdout[:350] + "\n...")

    print("\n========================================================")
    print("   [SUCCESS] Q-VALIDATE PHASE 3 PORTAL INTEGRATION VERIFIED CLEANLY!")
    print("========================================================\n")

if __name__ == "__main__":
    main()
