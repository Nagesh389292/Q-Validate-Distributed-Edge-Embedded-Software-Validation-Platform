from pydantic import BaseModel, Field
from typing import List, Optional, Dict

# Build Schemas
class CreateBuildRequest(BaseModel):
    build_id: str = Field(..., example="BUILD-2001")
    version: str = Field(..., example="4.3.0")
    git_commit: str = Field(..., example="e5f6a7b8c9d0")
    branch: str = Field(default="main", example="feature/mem-mgmt")

class BuildResponse(BaseModel):
    build_id: str
    version: str
    git_commit: str
    branch: str
    status: str
    created_at: str

# Device Control Schemas
class FaultInjectRequest(BaseModel):
    fault_type: str = Field(..., example="CPU_OVERLOAD")
    intensity: float = Field(default=95.0, example=95.0)

class DeviceStatusResponse(BaseModel):
    device_id: str
    name: str
    platform_type: str
    status: str
    firmware_version: str
    cpu_usage_pct: float
    memory_used_mb: float
    temperature_celsius: float

# Test Impact Analysis Schemas
class TIARequest(BaseModel):
    changed_files: List[str] = Field(..., example=["MemoryManager.cpp", "Firmware.cpp"])

class TIAResponse(BaseModel):
    changed_files: List[str]
    impacted_component_ids: List[str]
    selected_test_count: int
    selected_tests: List[Dict]

# Test Run Trigger Schemas
class TriggerTestRunRequest(BaseModel):
    build_id: str = Field(..., example="BUILD-1042")
    device_id: str = Field(default="DEVICE-001", example="DEVICE-001")
    suite_id: str = Field(default="SUITE-SANITY", example="SUITE-SANITY")
    max_retries: int = Field(default=1, example=1)

class TestRunResponse(BaseModel):
    run_id: str
    build_id: str
    device_id: str
    suite_id: str
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_sec: Optional[float] = 0.0
    total_tests: Optional[int] = 0
    passed_tests: Optional[int] = 0
    failed_tests: Optional[int] = 0
    skipped_tests: Optional[int] = 0
    results: Optional[List[Dict]] = []

# Defect Update Schema
class UpdateDefectRequest(BaseModel):
    status: str = Field(..., example="TRIAGED")
    root_cause: Optional[str] = Field(None, example="Memory pool boundary over-allocation confirmed")

class DefectResponse(BaseModel):
    defect_id: str
    title: str
    severity: str
    status: str
    component_name: str
    first_failing_build: str
    affected_tests: str
    root_cause: Optional[str] = None
    created_at: str
