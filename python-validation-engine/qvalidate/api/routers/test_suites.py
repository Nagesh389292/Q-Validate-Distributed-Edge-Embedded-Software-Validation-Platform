from fastapi import APIRouter
from typing import List
from qvalidate.db import DatabaseManager

router = APIRouter(prefix="/test-suites", tags=["Test Suite Catalog"])
db = DatabaseManager()

@router.get("", response_model=List[dict])
def get_all_test_suites():
    """List all available test suites."""
    return db.get_all_test_suites()
