from fastapi import APIRouter, HTTPException
from typing import List
from qvalidate.db import DatabaseManager
from qvalidate.api.schemas import UpdateDefectRequest

router = APIRouter(prefix="/defects", tags=["Defect & Issue Triage"])
db = DatabaseManager()

@router.get("", response_model=List[dict])
def get_all_defects():
    """List all auto-generated and triaged defect tickets."""
    return db.get_all_defects()

@router.get("/{defect_id}", response_model=dict)
def get_defect(defect_id: str):
    """Get details for a specific defect ticket."""
    d = db.get_defect(defect_id)
    if not d:
        raise HTTPException(status_code=404, detail=f"Defect {defect_id} not found")
    return d

@router.patch("/{defect_id}", response_model=dict)
def update_defect(defect_id: str, req: UpdateDefectRequest):
    """Update status or root cause analysis on a defect ticket."""
    d = db.get_defect(defect_id)
    if not d:
        raise HTTPException(status_code=404, detail=f"Defect {defect_id} not found")
    db.update_defect_status(defect_id, req.status, req.root_cause)
    return db.get_defect(defect_id)
