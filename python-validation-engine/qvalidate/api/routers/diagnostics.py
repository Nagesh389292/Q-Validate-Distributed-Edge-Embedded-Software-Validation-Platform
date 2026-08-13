from fastapi import APIRouter, HTTPException
from qvalidate.db import DatabaseManager
from qvalidate.reporter import Reporter
from qvalidate.models import TestRunSummary, TestCaseResult, TestStatus

router = APIRouter(prefix="/diagnostics", tags=["Failure Diagnostics & Triage"])
db = DatabaseManager()

@router.post("/triage/{run_id}", response_model=dict)
def trigger_automated_triage(run_id: str):
    """
    Trigger automated failure triage engine on a test run.
    Parses failure logs, groups failing test IDs, and generates a defect ticket.
    """
    run_data = db.get_test_run(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail=f"Test run {run_id} not found")
    
    results = []
    for r in run_data.get("results", []):
        results.append(TestCaseResult(
            test_id=r["test_id"],
            name=r.get("name", r["test_id"]),
            status=TestStatus(r["status"]),
            duration_sec=r.get("duration_sec", 0.0),
            actual_result=r.get("actual_result", ""),
            expected_result=r.get("expected_result", ""),
            device_id=run_data["device_id"],
            build_id=run_data["build_id"],
            error_log=r.get("error_log")
        ))

    summary = TestRunSummary(
        run_id=run_data["run_id"],
        build_id=run_data["build_id"],
        device_id=run_data["device_id"],
        suite_id=run_data["suite_id"],
        status=run_data["status"],
        start_time=0.0,
        end_time=0.0,
        total_tests=run_data.get("total_tests", len(results)),
        passed_tests=run_data.get("passed_tests", 0),
        failed_tests=run_data.get("failed_tests", 0),
        skipped_tests=run_data.get("skipped_tests", 0),
        results=results
    )

    tickets = Reporter.perform_failure_triage(summary)
    return {
        "run_id": run_id,
        "triaged_defects_created": len(tickets),
        "defects": [{"defect_id": t.defect_id, "title": t.title, "severity": t.severity} for t in tickets]
    }
