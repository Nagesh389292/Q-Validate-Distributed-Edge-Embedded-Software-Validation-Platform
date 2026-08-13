import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qvalidate.event_bus import EventBus, EventType
from qvalidate.capabilities import is_device_capable, DEVICE_FARM_CAPABILITIES
from qvalidate.scheduler import DistributedTestScheduler, SchedulerJob
from qvalidate.distributed_runner import DistributedTestWorkerPool
from qvalidate.db import DatabaseManager

def test_event_bus_publish_subscribe():
    bus = EventBus()
    received = []

    def handler(evt):
        received.append(evt)

    bus.subscribe(EventType.TEST_QUEUED, handler)
    bus.publish(EventType.TEST_QUEUED, {"test_id": "DSP-012"}, device_id="DEVICE-002")

    assert len(received) > 0
    assert received[-1]["payload"]["test_id"] == "DSP-012"
    assert received[-1]["device_id"] == "DEVICE-002"

def test_hardware_capability_matching():
    dsp_caps = ["CPU", "MEMORY", "DSP"]
    ai_caps = ["CPU", "MEMORY", "AI_ACCELERATOR"]

    assert is_device_capable(dsp_caps, "DSP") is True
    assert is_device_capable(dsp_caps, "AI_ACCELERATOR") is False
    assert is_device_capable(ai_caps, "AI_ACCELERATOR") is True

def test_scheduler_priority_queue_and_allocation():
    db = DatabaseManager()
    scheduler = DistributedTestScheduler(db=db)

    job_low = SchedulerJob(test_id="MEM-003", build_id="BUILD-1042", suite_id="S1", required_capability="MEMORY", priority=1)
    job_high = SchedulerJob(test_id="AI-045", build_id="BUILD-1042", suite_id="S1", required_capability="AI_ACCELERATOR", priority=10)

    scheduler.submit_job(job_low)
    scheduler.submit_job(job_high)

    status = scheduler.get_queue_status()
    assert status["queue_depth"] == 2
    # High priority job must be at front of queue
    assert status["queued_jobs"][0]["test_id"] == "AI-045"

    allocated_dev = scheduler.allocate_device_for_job(job_high)
    assert allocated_dev is not None
    assert "AI_ACCELERATOR" in allocated_dev["capabilities"]

    scheduler.release_device(allocated_dev["device_id"])

def test_distributed_parallel_worker_pool():
    test_workload = [
        {"test_id": "BOOT-001", "name": "Boot Test", "required_capability": "CPU"},
        {"test_id": "DSP-012", "name": "DSP Test", "required_capability": "DSP"},
        {"test_id": "AI-045", "name": "AI Test", "required_capability": "AI_ACCELERATOR"},
    ]

    pool = DistributedTestWorkerPool(max_workers=5)
    res = pool.run_workload(test_workload, mode="PARALLEL")

    assert res["total_tests"] == 3
    assert res["passed_tests"] >= 2
    assert res["duration_sec"] > 0
    assert res["active_devices_used"] >= 1
