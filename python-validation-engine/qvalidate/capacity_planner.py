from typing import Dict
from qvalidate.farm_manager import DeviceFarmManager

class CapacityPlanner:
    """
    Capacity Planner Service for estimating workload execution duration and farm throughput.
    """
    def __init__(self, farm_manager: DeviceFarmManager = None):
        self.farm_manager = farm_manager or DeviceFarmManager()

    def estimate_completion_time(self, test_count: int, avg_duration_sec: float = 0.05) -> Dict:
        farm_metrics = self.farm_manager.get_farm_metrics()
        ready_devices = max(farm_metrics["ready_devices"], 1)
        total_devices = farm_metrics["total_devices"]

        total_workload_seconds = test_count * avg_duration_sec
        estimated_duration_sec = round(total_workload_seconds / ready_devices, 2)
        estimated_throughput_tps = round(ready_devices / avg_duration_sec, 2)

        return {
            "queued_test_count": test_count,
            "total_farm_nodes": total_devices,
            "active_ready_nodes": ready_devices,
            "avg_test_duration_sec": avg_duration_sec,
            "estimated_completion_seconds": estimated_duration_sec,
            "estimated_throughput_tps": estimated_throughput_tps
        }
