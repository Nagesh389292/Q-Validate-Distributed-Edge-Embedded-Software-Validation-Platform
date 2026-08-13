import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))

from qvalidate.farm_manager import DeviceFarmManager
from qvalidate.capacity_planner import CapacityPlanner

def main():
    print("\n========================================================================")
    print("   Q-VALIDATE — DEVICE FARM MANAGER SCALING BENCHMARK (PHASE 6A)        ")
    print("========================================================================\n")

    farm = DeviceFarmManager()
    planner = CapacityPlanner(farm_manager=farm)

    test_workload_size = 100
    scale_levels = [10, 25, 50, 100]

    print(f"Simulating Capacity Planning for {test_workload_size} Queued Tests across Farm Scales...\n")
    print(f"{'Farm Nodes':<12} | {'Ready Nodes':<12} | {'Est. Duration (s)':<20} | {'Throughput (tests/s)':<22}")
    print("-" * 75)

    for nodes in scale_levels:
        farm.scale_farm(target_nodes=nodes)
        est = planner.estimate_completion_time(test_count=test_workload_size, avg_duration_sec=0.05)
        
        print(f"{nodes:<12} | {est['active_ready_nodes']:<12} | {est['estimated_completion_seconds']:<20} | {est['estimated_throughput_tps']:<22}")

    print("\n========================================================================")
    print("        SCALABLE EDGE FARM CAPACITY BENCHMARK: COMPLETE!              ")
    print("========================================================================\n")

if __name__ == "__main__":
    main()
