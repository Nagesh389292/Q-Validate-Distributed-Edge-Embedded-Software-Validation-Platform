from fastapi import APIRouter, HTTPException
from qvalidate.db import DatabaseManager

router = APIRouter(prefix="/results", tags=["Test Results Catalog"])
db = DatabaseManager()

@router.get("/{run_id}", response_model=dict)
def get_run_results(run_id: str):
    """Retrieve detailed itemized test case results for a test run."""
    run = db.get_test_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Test run {run_id} not found")
    return {"run_id": run_id, "status": run["status"], "results": run.get("results", [])}
