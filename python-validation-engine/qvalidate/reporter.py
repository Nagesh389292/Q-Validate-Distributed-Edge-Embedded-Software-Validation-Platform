import uuid
from typing import List
from qvalidate.models import TestRunSummary, TestCaseResult, DefectTicket, TestStatus
from qvalidate.db import DatabaseManager

class Reporter:
    @staticmethod
    def print_summary(summary: TestRunSummary):
        print("\n" + "="*70)
        print(f"   Q-VALIDATE TEST RUN REPORT [{summary.run_id}]")
        print("="*70)
        print(f"Build Version : {summary.build_id}")
        print(f"Target Device : {summary.device_id}")
        print(f"Test Suite    : {summary.suite_id}")
        print(f"Run Duration  : {round(summary.end_time - summary.start_time, 2)}s")
        print(f"Status        : {'[ PASS ]' if summary.status == 'PASSED' else '[ FAIL ]'}")
        print("-" * 70)
        print(f"Total: {summary.total_tests} | Passed: {summary.passed_tests} | Failed: {summary.failed_tests} | Skipped: {summary.skipped_tests}")
        print("-" * 70)

        for res in summary.results:
            badge = "[ PASS ]" if res.status == TestStatus.PASS else "[ FAIL ]"
            print(f"  {badge} {res.test_id:<10} | {res.name:<35} | {res.duration_sec:.2f}s")
            if res.status != TestStatus.PASS:
                print(f"     -> Expected: {res.expected_result}")
                print(f"     -> Actual  : {res.actual_result}")

        print("="*70 + "\n")

    @staticmethod
    def perform_failure_triage(summary: TestRunSummary) -> List[DefectTicket]:
        db = DatabaseManager()
        created_tickets = []

        failed_results = [r for r in summary.results if r.status == TestStatus.FAIL]
        if not failed_results:
            return created_tickets

        # Group failing tests by probable component
        failed_test_ids = [r.test_id for r in failed_results]

        defect = DefectTicket(
            defect_id=f"DEFECT-{uuid.uuid4().hex[:6].upper()}",
            title=f"Regression detected in Build {summary.build_id}: {len(failed_results)} test(s) failed",
            severity="CRITICAL" if len(failed_results) >= 3 else "HIGH",
            status="OPEN",
            component_name="Memory / CPU Subsystem",
            first_failing_build=summary.build_id,
            affected_tests=failed_test_ids,
            root_cause=f"Automated Triage: {failed_results[0].test_id} failed with '{failed_results[0].actual_result}'"
        )
        db.create_defect(defect)
        created_tickets.append(defect)

        print(f"[TRIAGE AUTO-DEFECT GENERATED] Ticket {defect.defect_id}: {defect.title}")
        return created_tickets
