from fastapi import APIRouter
from typing import List
from qvalidate.db import DatabaseManager

router = APIRouter(prefix="/components", tags=["Component Catalog"])
db = DatabaseManager()

@router.get("", response_model=List[dict])
def get_all_components():
    """List all registered system components."""
    return db.get_all_components()
