import time
from typing import Dict

class PrometheusMetricsRegistry:
    """
    Prometheus Metrics Collector & Exporter for Q-Validate Platform.
    Exports standard Prometheus line format text for /metrics endpoint scraping.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PrometheusMetricsRegistry, cls).__new__(cls)
            cls._instance.test_runs_total = 0
            cls._instance.test_failures_total = 0
            cls._instance.device_faults_total = 0
            cls._instance.queue_depth = 0
            cls._instance.active_workers = 0
            cls._instance.test_durations = []
        return cls._instance

    def record_test_run(self, status: str, duration_sec: float):
        self.test_runs_total += 1
        if status in ("FAIL", "FAILED", "ERROR"):
            self.test_failures_total += 1
        self.test_durations.append(duration_sec)

    def record_fault_injection(self, fault_type: str):
        self.device_faults_total += 1

    def update_queue_metrics(self, depth: int, active_workers: int):
        self.queue_depth = depth
        self.active_workers = active_workers

    @staticmethod
    def generate_prometheus_text() -> str:
        # Generate official Prometheus Exposition Format (text/plain; version=0.0.4)
        lines = [
            "# HELP qvalidate_test_runs_total Total number of test suite execution runs",
            "# TYPE qvalidate_test_runs_total counter",
            f"qvalidate_test_runs_total {PrometheusMetricsRegistry().test_runs_total}",
            "",
            "# HELP qvalidate_test_failures_total Total number of failed test executions",
            "# TYPE qvalidate_test_failures_total counter",
            f"qvalidate_test_failures_total {PrometheusMetricsRegistry().test_failures_total}",
            "",
            "# HELP qvalidate_scheduler_queue_depth Current pending queue depth in scheduler",
            "# TYPE qvalidate_scheduler_queue_depth gauge",
            f"qvalidate_scheduler_queue_depth {PrometheusMetricsRegistry().queue_depth}",
            "",
            "# HELP qvalidate_worker_utilization Active parallel worker threads",
            "# TYPE qvalidate_worker_utilization gauge",
            f"qvalidate_worker_utilization {PrometheusMetricsRegistry().active_workers}",
            "",
            "# HELP qvalidate_device_faults_total Total hardware fault injection events",
            "# TYPE qvalidate_device_faults_total counter",
            f"qvalidate_device_faults_total {PrometheusMetricsRegistry().device_faults_total}",
            ""
        ]
        return "\n".join(lines)
