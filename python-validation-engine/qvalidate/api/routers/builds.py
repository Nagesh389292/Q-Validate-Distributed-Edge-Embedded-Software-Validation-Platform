from fastapi import APIRouter, HTTPException
from typing import List
from qvalidate.db import DatabaseManager
from qvalidate.api.schemas import CreateBuildRequest

router = APIRouter(prefix="/builds", tags=["Build Management"])
db = DatabaseManager()

@router.get("", response_model=List[dict])
def get_all_builds():
    """List all registered software builds."""
    return db.get_all_builds()

@router.post("", response_model=dict, status_code=201)
def create_build(req: CreateBuildRequest):
    """Register a new software build in the platform."""
    existing = db.get_build(req.build_id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Build {req.build_id} already exists")
    return db.create_build(req.build_id, req.version, req.git_commit, req.branch)

@router.get("/{build_id}", response_model=dict)
def get_build(build_id: str):
    """Get details for a specific build."""
    b = db.get_build(build_id)
    if not b:
        raise HTTPException(status_code=404, detail=f"Build {build_id} not found")
    return b
