import time
import uuid
import traceback
from typing import List, Callable, Dict, Optional
from qvalidate.models import TestCaseResult, TestRunSummary, TestStatus, MetricSample
from qvalidate.client import DeviceClient
from qvalidate.db import DatabaseManager

class TestRunner:
    """
    Test Discovery, Execution, & Regression Orchestrator.
    Supports execution priority, retry handling, timeouts, and cancellation.
    """
    def __init__(self, build_id: str = "BUILD-1042", device_id: str = "DEVICE-001", suite_id: str = "SUITE-FULL", max_retries: int = 1, timeout_sec: float = 30.0):
        self.build_id = build_id
        self.device_id = device_id
        self.suite_id = suite_id
        self.max_retries = max_retries
        self.timeout_sec = timeout_sec
        self.client = DeviceClient(device_id=device_id)
        self.db = DatabaseManager()
        self.registered_tests: List[Dict] = []
        self._is_cancelled = False

    def register_test(self, test_id: str, name: str, expected_result: str, func: Callable[[DeviceClient], str], priority: int = 1):
        self.registered_tests.append({
            "test_id": test_id,
            "name": name,
            "expected_result": expected_result,
            "func": func,
            "priority": priority
        })

    def cancel(self):
        self._is_cancelled = True

    def run_suite(self) -> TestRunSummary:
        run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"
        start_time = time.time()
        results: List[TestCaseResult] = []

        # Sort tests by priority (higher priority number runs first)
        sorted_tests = sorted(self.registered_tests, key=lambda x: x.get("priority", 1), reverse=True)

        passed = 0
        failed = 0
        skipped = 0

        # Mark build as VALIDATING
        self.db.update_build_status(self.build_id, "VALIDATING")
        self.db.create_test_run(run_id, self.build_id, self.device_id, self.suite_id)
        self.db.update_test_run_status(run_id, "RUNNING")

        # Ensure device powered on before test suite starts
        self.client.power_on()

        for t in sorted_tests:
            if self._is_cancelled:
                skipped += 1
                results.append(TestCaseResult(
                    test_id=t["test_id"],
                    name=t["name"],
                    status=TestStatus.SKIP,
                    duration_sec=0.0,
                    actual_result="Execution cancelled by user request",
                    expected_result=t["expected_result"],
                    device_id=self.device_id,
                    build_id=self.build_id
                ))
                continue

            test_id = t["test_id"]
            name = t["name"]
            expected = t["expected_result"]
            func = t["func"]

            t_start = time.time()
            metrics_before = self.client.collect_metrics(count=2)
            
            attempts = 0
            success = False
            last_error_log = None
            actual_msg = ""

            while attempts <= self.max_retries and not success:
                attempts += 1
                try:
                    actual_msg = func(self.client)
                    success = True
                    last_error_log = None
                except Exception as e:
                    actual_msg = f"Attempt {attempts} Failed: {str(e)}"
                    last_error_log = traceback.format_exc()
                    if attempts <= self.max_retries:
                        time.sleep(0.1) # Retry delay

            t_dur = round(time.time() - t_start, 3)

            if success:
                status = TestStatus.PASS
                passed += 1
            else:
                status = TestStatus.FAIL
                failed += 1

            metrics_after = self.client.collect_metrics(count=2)

            results.append(TestCaseResult(
                test_id=test_id,
                name=name,
                status=status,
                duration_sec=t_dur,
                actual_result=actual_msg,
                expected_result=expected,
                device_id=self.device_id,
                build_id=self.build_id,
                error_log=last_error_log,
                metrics=metrics_before + metrics_after
            ))

        end_time = time.time()
        
        if self._is_cancelled:
            overall_status = "CANCELLED"
        else:
            overall_status = "PASSED" if failed == 0 else "FAILED"

        # Update build state based on test outcome
        if overall_status == "PASSED":
            self.db.update_build_status(self.build_id, "PASSED")
        elif overall_status == "FAILED":
            self.db.update_build_status(self.build_id, "FAILED")

        summary = TestRunSummary(
            run_id=run_id,
            build_id=self.build_id,
            device_id=self.device_id,
            suite_id=self.suite_id,
            status=overall_status,
            start_time=start_time,
            end_time=end_time,
            total_tests=len(self.registered_tests),
            passed_tests=passed,
            failed_tests=failed,
            skipped_tests=skipped,
            results=results
        )

        self.db.save_test_run(summary)
        return summary
