import time
import uuid
import concurrent.futures
from typing import List, Dict
from qvalidate.db import DatabaseManager
from qvalidate.client import DeviceClient
from qvalidate.models import TestRunSummary, TestCaseResult, TestStatus, DefectTicket
from qvalidate.event_bus import EventBus, EventType
from qvalidate.capabilities import DEVICE_FARM_CAPABILITIES, is_device_capable
from qvalidate.tracing import Tracer
from qvalidate.metrics import PrometheusMetricsRegistry
from qvalidate.logging_config import get_structured_logger

logger = get_structured_logger("qvalidate.distributed_runner")

class DistributedTestWorkerPool:
    """
    Distributed Test Worker Pool executing validation workloads concurrently across
    10 simulated C++ edge devices with OpenTelemetry tracing, Prometheus metrics, and structured logs.
    """
    def __init__(self, build_id: str = "BUILD-1042", suite_id: str = "SUITE-DISTRIBUTED", max_workers: int = 10):
        self.build_id = build_id
        self.suite_id = suite_id
        self.max_workers = max_workers
        self.db = DatabaseManager()
        self.event_bus = EventBus()
        self.tracer = Tracer()
        self.metrics = PrometheusMetricsRegistry()
        self.is_shutting_down = False
        self.processed_task_hashes = set()

    def process_task_idempotent(self, run_id: str, test_id: str) -> bool:
        """Returns True if task is new, False if duplicate payload already processed."""
        task_hash = f"{run_id}:{test_id}"
        if task_hash in self.processed_task_hashes:
            logger.info(f"Idempotency Guard: Duplicate task payload {task_hash} ignored.")
            return False
        self.processed_task_hashes.add(task_hash)
        return True

    def execute_single_test_task(self, args) -> Dict:
        test_info, device_id, run_id, root_trace_id, root_span_id = args
        test_id = test_info["test_id"]
        name = test_info["name"]
        req_cap = test_info.get("required_capability", "CPU")

        t_start = time.time()
        
        # Start Worker OpenTelemetry Span
        worker_span = self.tracer.start_span(
            name=f"worker_execution_{test_id}",
            trace_id=root_trace_id,
            parent_span_id=root_span_id,
            service_name="qvalidate-worker"
        )
        worker_span.set_attribute("test_id", test_id)
        worker_span.set_attribute("device_id", device_id)
        worker_span.set_attribute("run_id", run_id)
        worker_span.set_attribute("required_capability", req_cap)

        # Structured Log: Test Task Started
        logger.info(f"Worker assigned test {test_id} on {device_id} (Run: {run_id})", extra={
            "run_id": run_id, "test_id": test_id, "device_id": device_id, "trace_id": root_trace_id
        })

        # Reserve device node
        self.db.reserve_device(device_id)
        self.event_bus.publish(EventType.DEVICE_ALLOCATED, {"test_id": test_id, "device_id": device_id, "run_id": run_id}, device_id=device_id)

        try:
            # Child Span: C++ Device Runtime gRPC invocation
            cxx_span = self.tracer.start_span(
                name=f"cxx_runtime_grpc_{device_id}",
                trace_id=root_trace_id,
                parent_span_id=worker_span.span_id,
                service_name="qvalidate-cxx-runtime"
            )
            cxx_span.set_attribute("device_id", device_id)

            client = DeviceClient(device_id=device_id)
            client.power_on()

            # Simulate workload processing
            time.sleep(0.04)

            # Capability verification check
            caps = DEVICE_FARM_CAPABILITIES.get(device_id, ["CPU", "MEMORY"])
            if not is_device_capable(caps, req_cap):
                status = TestStatus.FAIL
                msg = f"Capability Mismatch: Test {test_id} requires {req_cap}, but device {device_id} supports {caps}"
                worker_span.set_status_error(msg)
                cxx_span.set_status_error(msg)
                
                # Auto-create defect for failed test
                defect = DefectTicket(
                    defect_id=f"DEF-{uuid.uuid4().hex[:6].upper()}",
                    title=f"Hardware Capability Mismatch on {device_id} for {test_id}",
                    severity="HIGH",
                    status="OPEN",
                    component_name=req_cap,
                    first_failing_build=self.build_id,
                    affected_tests=[test_id],
                    root_cause=msg
                )
                self.db.create_defect(defect)
            else:
                status = TestStatus.PASS
                msg = f"Test {test_id} executed successfully on {device_id} ({req_cap} capable)"

            cxx_span.finish()
            t_dur = round(time.time() - t_start, 3)

            # Record Prometheus Metrics
            self.metrics.record_test_run(status=status.value, duration_sec=t_dur)

            # Structured Log: Test Task Completed
            logger.info(f"Test {test_id} finished with status {status.value} in {t_dur}s", extra={
                "run_id": run_id, "test_id": test_id, "device_id": device_id, "status": status.value, "trace_id": root_trace_id
            })

            return {
                "test_id": test_id,
                "name": name,
                "status": status,
                "duration_sec": t_dur,
                "device_id": device_id,
                "actual_result": msg,
                "expected_result": test_info.get("expected_result", "Success"),
                "trace_id": root_trace_id,
                "span_id": worker_span.span_id
            }
        except Exception as e:
            worker_span.set_status_error(str(e))
            logger.error(f"Worker task error for {test_id}: {e}", extra={"run_id": run_id, "test_id": test_id})
            return {
                "test_id": test_id,
                "name": name,
                "status": TestStatus.FAIL,
                "duration_sec": 0.05,
                "device_id": device_id,
                "actual_result": f"Execution Error: {e}",
                "expected_result": "Success",
                "trace_id": root_trace_id
            }
        finally:
            worker_span.finish()
            # Always release device node lock
            self.db.release_device(device_id)
            self.event_bus.publish(EventType.DEVICE_RELEASED, {"test_id": test_id, "device_id": device_id, "run_id": run_id}, device_id=device_id)

    def run_workload(self, test_tasks: List[Dict], mode: str = "PARALLEL") -> Dict:
        run_id = f"RUN-DIST-{uuid.uuid4().hex[:6].upper()}"
        start_time = time.time()
        
        # Start Root Distributed Trace Span for entire Test Run
        root_span = self.tracer.start_span(
            name=f"test_run_workflow_{run_id}",
            service_name="qvalidate-control-plane"
        )
        root_span.set_attribute("run_id", run_id)
        root_span.set_attribute("build_id", self.build_id)
        root_span.set_attribute("mode", mode)
        root_span.set_attribute("total_tests", str(len(test_tasks)))

        # Update Prometheus Queue Metrics
        self.metrics.update_queue_metrics(depth=len(test_tasks), active_workers=self.max_workers if mode == "PARALLEL" else 1)

        devices = self.db.get_all_devices()
        device_ids = [d["device_id"] for d in devices]

        # Map tests to target device nodes round-robin with trace context
        task_args = []
        for idx, t in enumerate(test_tasks):
            assigned_device = device_ids[idx % len(device_ids)]
            task_args.append((t, assigned_device, run_id, root_span.trace_id, root_span.span_id))

        results_data = []
        
        if mode == "PARALLEL":
            num_workers = min(self.max_workers, len(device_ids))
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
                results_data = list(executor.map(self.execute_single_test_task, task_args))
        else:
            # Sequential execution (1 worker)
            for arg in task_args:
                results_data.append(self.execute_single_test_task(arg))

        end_time = time.time()
        total_duration = round(end_time - start_time, 3)
        passed_count = sum(1 for r in results_data if r["status"] == TestStatus.PASS)
        failed_count = sum(1 for r in results_data if r["status"] == TestStatus.FAIL)

        tests_per_sec = round(len(test_tasks) / total_duration, 2) if total_duration > 0 else 0.0

        self.metrics.update_queue_metrics(depth=0, active_workers=0)
        root_span.finish()

        return {
            "run_id": run_id,
            "trace_id": root_span.trace_id,
            "mode": mode,
            "total_tests": len(test_tasks),
            "passed_tests": passed_count,
            "failed_tests": failed_count,
            "duration_sec": total_duration,
            "tests_per_sec": tests_per_sec,
            "active_devices_used": len(set(a[1] for a in task_args)),
            "results": results_data
        }
