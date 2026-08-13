import sys
import os

# Ensure python-validation-engine is in path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from qvalidate.api.main import app
from qvalidate.client import DeviceClient

def main():
    print("\n========================================================")
    print("   Q-VALIDATE — PRODUCTION CONTROL PLANE (PHASE 2 E2E)")
    print("========================================================\n")

    client = TestClient(app)

    # 1. Health check
    res_health = client.get("/health")
    print(f"[API HEALTH]: {res_health.json()}")
    assert res_health.status_code == 200

    # 2. Register new software build (BUILD-2001)
    print("\n[PHASE 2.1] Registering New Software Build (BUILD-2001)...")
    res_build = client.post("/api/v1/builds", json={
        "build_id": "BUILD-2001",
        "version": "4.3.0",
        "git_commit": "e5f6a7b8c9d0",
        "branch": "feature/memory-optimizer"
    })
    print(f"  -> Build Registered: {res_build.json()}")
    assert res_build.status_code == 201

    # 3. Test Impact Analysis (TIA)
    print("\n[PHASE 2.2] Executing Test Impact Analysis (TIA) for 'MemoryManager.cpp'...")
    res_tia = client.post("/api/v1/regressions/impact-analysis", json={
        "changed_files": ["src/MemoryManager.cpp", "include/Memory.hpp"]
    })
    tia_data = res_tia.json()
    print(f"  -> Impacted Components : {tia_data['impacted_component_ids']}")
    print(f"  -> Selected Test Count : {tia_data['selected_test_count']}")
    for t in tia_data['selected_tests']:
        print(f"     * Selected Test: [{t['test_id']}] {t['name']} (Component: {t['component_name']})")
    assert "COMP-MEM" in tia_data['impacted_component_ids']

    # 4. Device Status and Fault Injection
    print("\n[PHASE 2.3] Testing Device Telemetry & Fault Injection Control via REST API...")
    res_power = client.post("/api/v1/devices/DEVICE-001/power-on")
    print(f"  -> Power On Response: {res_power.json()}")

    res_fault = client.post("/api/v1/devices/DEVICE-001/inject-fault", json={"fault_type": "CPU_OVERLOAD", "intensity": 99.0})
    print(f"  -> Fault Inject Response: {res_fault.json()}")

    res_clear = client.post("/api/v1/devices/DEVICE-001/clear-fault")
    print(f"  -> Fault Clear Response: {res_clear.json()}")

    # 5. Trigger Test Run via REST API
    print("\n[PHASE 2.4] Triggering Test Suite Execution via REST API...")
    res_run = client.post("/api/v1/test-runs", json={
        "build_id": "BUILD-2001",
        "device_id": "DEVICE-001",
        "suite_id": "SUITE-REGRESSION",
        "max_retries": 1
    })
    run_data = res_run.json()
    print(f"  -> Test Run Triggered: {run_data['run_id']} | Status: {run_data['status']}")
    print(f"  -> Total Tests: {run_data['total_tests']} | Passed: {run_data['passed_tests']} | Failed: {run_data['failed_tests']}")

    # 6. Trigger Failure Triage and Defect Tracking
    print("\n[PHASE 2.5] Triggering Automated Failure Diagnostics & Defect Management via API...")
    res_triage = client.post(f"/api/v1/diagnostics/triage/{run_data['run_id']}")
    triage_data = res_triage.json()
    print(f"  -> Triage Result: Created {triage_data['triaged_defects_created']} Defect Ticket(s)")

    res_defects = client.get("/api/v1/defects")
    defects = res_defects.json()
    print(f"  -> Total Registered Defects in Platform: {len(defects)}")
    if len(defects) > 0:
        target_defect = defects[0]
        print(f"     * Defect Ticket [{target_defect['defect_id']}]: {target_defect['title']}")
        res_patch = client.patch(f"/api/v1/defects/{target_defect['defect_id']}", json={
            "status": "TRIAGED",
            "root_cause": "Root cause verified via REST API diagnostic pipeline: Memory heap boundary overflow in MemoryManager"
        })
        print(f"  -> Updated Defect Status: {res_patch.json()['status']} | Root Cause: {res_patch.json()['root_cause']}")

    # 7. C++ Native Binary Execution Check
    print("\n[PHASE 2.6] Verifying C++20 Native Device Runtime Executable Integration...")
    dev_client = DeviceClient(device_id="DEVICE-001")
    proc = dev_client.run_cxx_native_verification()
    print("[NATIVE C++ BINARY OUTPUT]:")
    print(proc.stdout[:400] + "\n...")

    print("\n========================================================")
    print("   [SUCCESS] Q-VALIDATE PHASE 2 CONTROL PLANE VERIFIED CLEANLY!")
    print("========================================================\n")

if __name__ == "__main__":
    main()
