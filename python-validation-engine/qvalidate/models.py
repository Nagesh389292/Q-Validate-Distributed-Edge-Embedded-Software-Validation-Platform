from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import time

class TestStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"

class DeviceState(str, Enum):
    POWERED_OFF = "POWERED_OFF"
    BOOTING = "BOOTING"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    ERROR = "ERROR"

@dataclass
class DeviceStatus:
    device_id: str
    state: DeviceState
    firmware_version: str
    uptime_seconds: float
    cpu_usage_pct: float
    memory_used_mb: float
    memory_total_mb: float
    temperature_celsius: float
    is_healthy: bool
    active_fault: str = "NONE"

@dataclass
class MetricSample:
    timestamp: float
    cpu_pct: float
    memory_mb: float
    temp_celsius: float

@dataclass
class TestCaseResult:
    test_id: str
    name: str
    status: TestStatus
    duration_sec: float
    actual_result: str
    expected_result: str
    device_id: str
    build_id: str
    error_log: Optional[str] = None
    metrics: List[MetricSample] = field(default_factory=list)

@dataclass
class TestRunSummary:
    run_id: str
    build_id: str
    device_id: str
    suite_id: str
    status: str
    start_time: float
    end_time: float
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    results: List[TestCaseResult] = field(default_factory=list)

@dataclass
class DefectTicket:
    defect_id: str
    title: str
    severity: str
    status: str
    component_name: str
    first_failing_build: str
    affected_tests: List[str]
    root_cause: str
    created_at: float = field(default_factory=time.time)
