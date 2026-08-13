import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from qvalidate.distributed_runner import DistributedTestWorkerPool
from qvalidate.db import DatabaseManager

def main():
    print("\n========================================================================")
    print("   Q-VALIDATE — DISTRIBUTED PARALLEL EXECUTION BENCHMARK (PHASE 4)")
    print("========================================================================\n")

    db = DatabaseManager()

    # Generate deterministic 50-test workload with varying capability requirements
    base_tests = [
        {"test_id": "BOOT-001", "name": "Cold Boot Sanity Check", "required_capability": "CPU"},
        {"test_id": "MEM-003", "name": "Dynamic Memory Allocation", "required_capability": "MEMORY"},
        {"test_id": "CPU-007", "name": "Multicore Load Stress", "required_capability": "CPU"},
        {"test_id": "DSP-012", "name": "Hexagon DSP FFT Processing", "required_capability": "DSP"},
        {"test_id": "AI-045", "name": "ResNet-50 Neural Inference", "required_capability": "AI_ACCELERATOR"},
    ]

    test_workload = []
    for i in range(10): # 10 iterations = 50 total test cases
        for bt in base_tests:
            test_workload.append({
                "test_id": f"{bt['test_id']}-#{i+1}",
                "name": f"{bt['name']} (Batch #{i+1})",
                "required_capability": bt["required_capability"],
                "expected_result": "Success"
            })

    pool = DistributedTestWorkerPool(build_id="BUILD-DIST-100", suite_id="SUITE-BENCHMARK", max_workers=10)

    # 1. Sequential Execution (1 Worker)
    print(f"[BENCHMARK 1/2] Running {len(test_workload)} Test Cases in SEQUENTIAL Mode (1 Worker)...")
    res_seq = pool.run_workload(test_workload, mode="SEQUENTIAL")
    print(f"  -> Sequential Execution Time : {res_seq['duration_sec']:.2f} seconds")
    print(f"  -> Throughput                : {res_seq['tests_per_sec']} tests/second")
    print(f"  -> Passed: {res_seq['passed_tests']} | Failed: {res_seq['failed_tests']}")

    # 2. Parallel Execution (10 Workers across 10 Device Nodes)
    print(f"\n[BENCHMARK 2/2] Running {len(test_workload)} Test Cases in PARALLEL Mode (10 Workers / 10 Devices)...")
    res_par = pool.run_workload(test_workload, mode="PARALLEL")
    print(f"  -> Parallel Execution Time   : {res_par['duration_sec']:.2f} seconds")
    print(f"  -> Throughput                : {res_par['tests_per_sec']} tests/second")
    print(f"  -> Active Devices Utilized   : {res_par['active_devices_used']} Edge Nodes")
    print(f"  -> Passed: {res_par['passed_tests']} | Failed: {res_par['failed_tests']}")

    # Performance Speedup Analysis
    speedup = round(res_seq['duration_sec'] / res_par['duration_sec'], 2) if res_par['duration_sec'] > 0 else 1.0

    print("\n========================================================================")
    print("                 BENCHMARK PERFORMANCE COMPARISON                       ")
    print("========================================================================")
    print(f" Total Test Cases        : {len(test_workload)} Tests")
    print(f" Sequential Duration     : {res_seq['duration_sec']:.2f}s")
    print(f" Parallel 10x Duration   : {res_par['duration_sec']:.2f}s")
    print(f" Execution Speedup Ratio : {speedup}x Parallel Acceleration")
    print("========================================================================\n")

if __name__ == "__main__":
    main()
