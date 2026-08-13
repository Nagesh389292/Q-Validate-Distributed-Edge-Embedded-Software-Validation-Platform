import sys
import os
import time
import statistics
from typing import List, Dict

sys.path.insert(0, os.path.dirname(__file__))

from qvalidate.db import DatabaseManager
from qvalidate.farm_manager import DeviceFarmManager
from qvalidate.capacity_planner import CapacityPlanner
from qvalidate.distributed_runner import DistributedTestWorkerPool

def run_real_stress_test(num_devices: int, test_count: int = 50) -> Dict:
    db = DatabaseManager()
    farm = DeviceFarmManager(db=db)
    farm.scale_farm(num_devices)
    
    # Sync database devices to match scale
    capabilities_options = [
        ["CPU", "MEMORY", "AI_ACCELERATOR"],
        ["CPU", "MEMORY", "DSP"],
        ["CPU", "MEMORY", "NETWORK"],
        ["CPU", "MEMORY", "DSP", "AI_ACCELERATOR"]
    ]
    for i in range(1, num_devices + 1):
        dev_id = f"DEVICE-{i:03d}"
        caps = capabilities_options[(i - 1) % len(capabilities_options)]
        db.upsert_device(dev_id, f"Node #{i}", "READY", caps)

    # Generate real test suite workload
    test_cases = []
    test_types = ["BOOT-001", "DSP-012", "AI-045", "MEM-003", "CPU-101", "NET-202"]
    for i in range(test_count):
        test_id = test_types[i % len(test_types)]
        test_cases.append({
            "test_id": f"{test_id}_{i:03d}",
            "name": f"Validation Test {i+1}",
            "required_capabilities": ["CPU", "MEMORY"] if i % 2 == 0 else ["DSP"]
        })

    # Execute REAL parallel worker pool across actual device nodes
    worker_pool = DistributedTestWorkerPool(build_id="BUILD-STRESS-600", max_workers=min(num_devices, 30))
    run_id = f"RUN-STRESS-{num_devices}NODES-{int(time.time())}"

    latencies_ms = []
    start_time = time.time()

    results_summary = worker_pool.run_workload(test_tasks=test_cases, mode="PARALLEL")
    results = results_summary["results"]

    end_time = time.time()
    wall_clock_sec = round(end_time - start_time, 3)

    for r in results:
        dur_ms = r.get("duration_sec", 0.05) * 1000.0
        latencies_ms.append(dur_ms)

    passed_count = sum(1 for r in results if r["status"].value == "PASS" or r["status"] == "PASS")
    failed_count = sum(1 for r in results if r["status"].value == "FAIL" or r["status"] == "FAIL")

    real_tps = round(len(results) / wall_clock_sec, 2) if wall_clock_sec > 0 else 0.0
    
    if latencies_ms:
        latencies_ms.sort()
        p50 = round(statistics.median(latencies_ms), 1)
        p95 = round(latencies_ms[int(len(latencies_ms) * 0.95)], 1)
    else:
        p50 = 0.0
        p95 = 0.0

    return {
        "num_devices": num_devices,
        "test_count": len(results),
        "passed": passed_count,
        "failed": failed_count,
        "wall_clock_sec": wall_clock_sec,
        "real_tps": real_tps,
        "p50_latency_ms": p50,
        "p95_latency_ms": p95
    }

def main():
    print("\n========================================================================")
    print("   Q-VALIDATE — PHASE 6B REAL DEVICE FARM STRESS BENCHMARK             ")
    print("========================================================================\n")

    scale_levels = [10, 25, 50, 100]
    workload_size = 50

    print(f"Executing REAL Parallel Execution Workload ({workload_size} Tests) across Farm Scales...\n")
    print(f"{'Farm Scale':<12} | {'Wall-Clock (s)':<16} | {'Passed/Failed':<16} | {'Real TPS':<12} | {'P50 (ms)':<10} | {'P95 (ms)':<10}")
    print("-" * 88)

    for scale in scale_levels:
        res = run_real_stress_test(num_devices=scale, test_count=workload_size)
        pf_str = f"{res['passed']}/{res['failed']}"
        print(f"{res['num_devices']:<12} | {res['wall_clock_sec']:<16} | {pf_str:<16} | {res['real_tps']:<12} | {res['p50_latency_ms']:<10} | {res['p95_latency_ms']:<10}")

    print("\n========================================================================")
    print("        REAL DEVICE FARM STRESS BENCHMARK: EXECUTION COMPLETE!          ")
    print("========================================================================\n")

if __name__ == "__main__":
    main()
