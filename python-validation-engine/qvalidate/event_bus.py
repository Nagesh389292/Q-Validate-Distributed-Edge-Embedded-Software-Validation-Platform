import time
import uuid
import json
from typing import Dict, List, Callable, Optional

class EventType:
    TEST_REQUESTED = "TEST_REQUESTED"
    TEST_QUEUED = "TEST_QUEUED"
    TEST_STARTED = "TEST_STARTED"
    TEST_COMPLETED = "TEST_COMPLETED"
    TEST_FAILED = "TEST_FAILED"
    TEST_CANCELLED = "TEST_CANCELLED"
    TEST_TIMEOUT = "TEST_TIMEOUT"
    DEVICE_ALLOCATED = "DEVICE_ALLOCATED"
    DEVICE_RELEASED = "DEVICE_RELEASED"
    REGRESSION_STARTED = "REGRESSION_STARTED"
    REGRESSION_COMPLETED = "REGRESSION_COMPLETED"

class EventBus:
    """
    Event-driven Kafka message bus publisher & subscriber engine for Q-Validate.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance.subscribers = {}
            cls._instance.event_log = []
        return cls._instance

    def subscribe(self, event_type: str, handler: Callable[[Dict], None]):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def publish(self, event_type: str, payload: Dict, run_id: Optional[str] = None, device_id: Optional[str] = None) -> Dict:
        event = {
            "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
            "event_type": event_type,
            "run_id": run_id,
            "device_id": device_id,
            "timestamp": time.time(),
            "payload": payload
        }
        self.event_log.append(event)
        
        # Dispatch to registered subscribers
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"[EVENT BUS ERROR] Handler failed for {event_type}: {e}")
        return event

    def get_events(self, limit: int = 50) -> List[Dict]:
        return self.event_log[-limit:]
