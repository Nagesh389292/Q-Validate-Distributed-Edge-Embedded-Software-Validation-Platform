from fastapi import APIRouter
from typing import List
from qvalidate.db import DatabaseManager

router = APIRouter(prefix="/test-cases", tags=["Test Catalog"])
db = DatabaseManager()

@router.get("", response_model=List[dict])
def get_all_test_cases():
    """List all available test cases."""
    return db.get_all_test_cases()
