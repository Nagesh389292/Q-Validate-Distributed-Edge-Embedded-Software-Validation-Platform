import sys
import os
import time
import statistics
from typing import Dict

sys.path.insert(0, os.path.dirname(__file__))

from qvalidate.db import DatabaseManager
from qvalidate.farm_manager import DeviceFarmManager
from qvalidate.distributed_runner import DistributedTestWorkerPool

def execute_benchmark_pass(backend_type: str, num_devices: int, test_count: int = 50) -> Dict:
    os.environ["DATABASE_BACKEND"] = backend_type
    db = DatabaseManager(backend=backend_type)
    farm = DeviceFarmManager(db=db)
    farm.scale_farm(num_devices)
    
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

    test_cases = []
    test_types = ["BOOT-001", "DSP-012", "AI-045", "MEM-003", "CPU-101", "NET-202"]
    for i in range(test_count):
        test_id = test_types[i % len(test_types)]
        test_cases.append({
            "test_id": f"{test_id}_{i:03d}",
            "name": f"Validation Test {i+1}",
            "required_capabilities": ["CPU", "MEMORY"] if i % 2 == 0 else ["DSP"]
        })

    worker_pool = DistributedTestWorkerPool(build_id=f"BUILD-{backend_type.upper()}-600", max_workers=min(num_devices, 30))
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
        p50, p95 = 0.0, 0.0

    return {
        "backend": backend_type.upper(),
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
    print("   Q-VALIDATE — PHASE 6C COMPARATIVE PERSISTENCE BENCHMARK             ")
    print("========================================================================\n")

    scale_levels = [10, 25, 50, 100]
    workload_size = 50

    print(f"Rerunning Identical Workload ({workload_size} Tests) across SQLite vs PostgreSQL...\n")
    print(f"{'Nodes':<6} | {'Backend':<10} | {'Wall-Clock (s)':<16} | {'Real TPS':<12} | {'P50 (ms)':<10} | {'P95 (ms)':<10}")
    print("-" * 75)

    for scale in scale_levels:
        res_sqlite = execute_benchmark_pass("sqlite", num_devices=scale, test_count=workload_size)
        print(f"{scale:<6} | {'SQLITE':<10} | {res_sqlite['wall_clock_sec']:<16} | {res_sqlite['real_tps']:<12} | {res_sqlite['p50_latency_ms']:<10} | {res_sqlite['p95_latency_ms']:<10}")
        
        # Test PostgreSQL / Pool Fallback Abstraction
        res_pg = execute_benchmark_pass("postgres", num_devices=scale, test_count=workload_size)
        print(f"{scale:<6} | {'POSTGRES':<10} | {res_pg['wall_clock_sec']:<16} | {res_pg['real_tps']:<12} | {res_pg['p50_latency_ms']:<10} | {res_pg['p95_latency_ms']:<10}")
        print("-" * 75)

    print("\n========================================================================")
    print("     COMPARATIVE PERSISTENCE BENCHMARK: EXECUTION COMPLETE!             ")
    print("========================================================================\n")

if __name__ == "__main__":
    main()
