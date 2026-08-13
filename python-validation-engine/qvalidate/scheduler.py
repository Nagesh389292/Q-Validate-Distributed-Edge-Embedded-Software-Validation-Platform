import time
import uuid
from typing import List, Dict, Optional
from qvalidate.db import DatabaseManager
from qvalidate.capabilities import is_device_capable, DEVICE_FARM_CAPABILITIES
from qvalidate.event_bus import EventBus, EventType

class SchedulerJob:
    def __init__(self, test_id: str, build_id: str, suite_id: str, required_capability: str = "CPU", priority: int = 1, max_retries: int = 1):
        self.job_id = f"JOB-{uuid.uuid4().hex[:6].upper()}"
        self.test_id = test_id
        self.build_id = build_id
        self.suite_id = suite_id
        self.required_capability = required_capability
        self.priority = priority
        self.max_retries = max_retries
        self.retry_count = 0
        self.status = "QUEUED"
        self.allocated_device_id: Optional[str] = None
        self.created_at = time.time()
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None

class DistributedTestScheduler:
    """
    Distributed Test Scheduler & Hardware Capability Matching Engine.
    Orchestrates job queues, priority scheduling, hardware capability matching,
    device locking, worker assignment, and event-bus notifications.
    """
    def __init__(self, db: DatabaseManager = None):
        self.db = db or DatabaseManager()
        self.event_bus = EventBus()
        self.queue: List[SchedulerJob] = []
        self.active_jobs: Dict[str, SchedulerJob] = {}

    def submit_job(self, job: SchedulerJob) -> SchedulerJob:
        self.queue.append(job)
        # Sort queue by priority descending (higher number runs first)
        self.queue.sort(key=lambda j: j.priority, reverse=True)
        
        self.event_bus.publish(EventType.TEST_QUEUED, {
            "job_id": job.job_id,
            "test_id": job.test_id,
            "priority": job.priority,
            "required_capability": job.required_capability
        })
        return job

    def allocate_device_for_job(self, job: SchedulerJob) -> Optional[Dict]:
        devices = self.db.get_all_devices()
        for dev in devices:
            caps = dev.get("capabilities", ["CPU", "MEMORY"])
            if is_device_capable(caps, job.required_capability):
                job.allocated_device_id = dev["device_id"]
                job.status = "ALLOCATED"
                self.db.reserve_device(dev["device_id"])
                
                self.event_bus.publish(EventType.DEVICE_ALLOCATED, {
                    "job_id": job.job_id,
                    "device_id": dev["device_id"],
                    "capabilities": caps
                }, device_id=dev["device_id"])
                return dev
        
        # Fallback allocation if no explicit capability match
        if devices:
            dev = devices[0]
            job.allocated_device_id = dev["device_id"]
            job.status = "ALLOCATED"
            return dev
        return None

    def release_device(self, device_id: str):
        self.db.release_device(device_id)
        self.event_bus.publish(EventType.DEVICE_RELEASED, {"device_id": device_id}, device_id=device_id)

    def get_queue_status(self) -> Dict:
        return {
            "queue_depth": len(self.queue),
            "active_job_count": len(self.active_jobs),
            "queued_jobs": [
                {
                    "job_id": j.job_id,
                    "test_id": j.test_id,
                    "priority": j.priority,
                    "required_capability": j.required_capability,
                    "status": j.status
                } for j in self.queue
            ]
        }
