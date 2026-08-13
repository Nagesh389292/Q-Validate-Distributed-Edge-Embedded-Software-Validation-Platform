import time
import uuid
import json
from typing import List, Dict, Optional
from qvalidate.db import DatabaseManager
from qvalidate.event_bus import EventBus, EventType

class DeviceState:
    PROVISIONING = "PROVISIONING"
    BOOTING = "BOOTING"
    READY = "READY"
    ALLOCATED = "ALLOCATED"
    TESTING = "TESTING"
    DEGRADED = "DEGRADED"
    ERROR = "ERROR"
    DIAGNOSTICS = "DIAGNOSTICS"
    RECOVERY = "RECOVERY"

class DeviceProfile:
    def __init__(self, device_id: str, name: str, architecture: str, capabilities: List[str], firmware: str = "4.2.1", memory_mb: int = 4096, cpu_cores: int = 8):
        self.device_id = device_id
        self.name = name
        self.architecture = architecture # ARM64_SIM, X86_64_SIM, HEXAGON_DSP_SIM, NPU_SIM
        self.capabilities = capabilities
        self.firmware = firmware
        self.memory_mb = memory_mb
        self.cpu_cores = cpu_cores
        self.status = DeviceState.READY
        self.is_reserved = False
        self.last_heartbeat = time.time()
        
        # Phase 6B: Dynamic Device Health Scoring
        self.health_score: float = 100.0 # 0.0 to 100.0
        self.test_failures_count: int = 0
        self.fault_injections_count: int = 0
        self.avg_response_latency_ms: float = 15.0

    def calculate_health_score(self) -> float:
        """Calculates dynamic health score based on failure rate, faults, and latency."""
        failure_penalty = self.test_failures_count * 12.0
        fault_penalty = self.fault_injections_count * 15.0
        latency_penalty = max(0.0, (self.avg_response_latency_ms - 20.0) * 0.5)
        
        score = max(0.0, round(100.0 - failure_penalty - fault_penalty - latency_penalty, 1))
        self.health_score = score
        
        if score < 50.0 and self.status == DeviceState.READY:
            self.status = DeviceState.DEGRADED
        return score

    def record_test_result(self, passed: bool, latency_ms: float):
        if not passed:
            self.test_failures_count += 1
        self.avg_response_latency_ms = round((self.avg_response_latency_ms * 0.7) + (latency_ms * 0.3), 2)
        self.calculate_health_score()

class DeviceFarmManager:
    """
    Enterprise Device Farm Manager Service.
    Handles dynamic node provisioning, lifecycle state transitions, automatic
    device health scoring, degraded isolation, and capability indexing.
    """
    _instance = None

    def __new__(cls, db: DatabaseManager = None):
        if cls._instance is None:
            cls._instance = super(DeviceFarmManager, cls).__new__(cls)
            cls._instance.db = db or DatabaseManager()
            cls._instance.event_bus = EventBus()
            cls._instance.farm: Dict[str, DeviceProfile] = {}
            cls._instance.init_farm()
        return cls._instance

    def init_farm(self, node_count: int = 25):
        """Provision simulated edge device farm with dynamic hardware profiles."""
        self.farm.clear()
        
        architectures = ["ARM64_SIM", "HEXAGON_DSP_SIM", "NPU_SIM", "X86_64_SIM"]
        capability_sets = [
            ["CPU", "MEMORY", "AI_ACCELERATOR"],
            ["CPU", "MEMORY", "DSP"],
            ["CPU", "MEMORY", "NETWORK"],
            ["CPU", "MEMORY", "DSP", "AI_ACCELERATOR"]
        ]

        for i in range(1, node_count + 1):
            dev_id = f"DEVICE-{i:03d}"
            arch = architectures[(i - 1) % len(architectures)]
            caps = capability_sets[(i - 1) % len(capability_sets)]
            mem = 2048 if "DSP" in caps else (8192 if "AI_ACCELERATOR" in caps else 4096)
            cores = 4 if "DSP" in caps else 8
            
            profile = DeviceProfile(
                device_id=dev_id,
                name=f"Snapdragon Edge Node #{i:03d}",
                architecture=arch,
                capabilities=caps,
                memory_mb=mem,
                cpu_cores=cores
            )
            self.farm[dev_id] = profile

    def scale_farm(self, target_nodes: int) -> int:
        """Scales the simulated device farm up to 25, 50, or 100 nodes."""
        self.init_farm(node_count=target_nodes)
        self.event_bus.publish("FARM_SCALED", {"node_count": target_nodes})
        return len(self.farm)

    def transition_state(self, device_id: str, new_state: str) -> bool:
        if device_id in self.farm:
            profile = self.farm[device_id]
            old_state = profile.status
            profile.status = new_state
            profile.last_heartbeat = time.time()
            
            self.event_bus.publish("DEVICE_STATE_TRANSITION", {
                "device_id": device_id,
                "old_state": old_state,
                "new_state": new_state
            }, device_id=device_id)
            return True
        return False

    def recover_degraded_device(self, device_id: str) -> bool:
        """Triggers dynamic diagnostic check and state recovery for degraded nodes."""
        if device_id in self.farm:
            profile = self.farm[device_id]
            self.transition_state(device_id, DeviceState.DIAGNOSTICS)
            time.sleep(0.01) # Simulate hardware self-test diagnostic
            profile.test_failures_count = 0
            profile.fault_injections_count = 0
            profile.avg_response_latency_ms = 15.0
            profile.health_score = 100.0
            self.transition_state(device_id, DeviceState.RECOVERY)
            time.sleep(0.01)
            self.transition_state(device_id, DeviceState.READY)
            return True
        return False

    def get_farm_metrics(self) -> Dict:
        total = len(self.farm)
        ready = sum(1 for p in self.farm.values() if p.status == DeviceState.READY and p.health_score >= 50.0)
        allocated = sum(1 for p in self.farm.values() if p.status in (DeviceState.ALLOCATED, DeviceState.TESTING))
        degraded = sum(1 for p in self.farm.values() if p.status == DeviceState.DEGRADED or p.health_score < 50.0)
        error = sum(1 for p in self.farm.values() if p.status == DeviceState.ERROR)
        
        avg_health = round(sum(p.health_score for p in self.farm.values()) / total, 1) if total > 0 else 100.0

        return {
            "total_devices": total,
            "ready_devices": ready,
            "allocated_devices": allocated,
            "degraded_devices": degraded,
            "error_devices": error,
            "avg_health_score": avg_health,
            "utilization_pct": round((allocated / total) * 100.0, 1) if total > 0 else 0.0
        }

    def get_all_device_profiles(self) -> List[Dict]:
        return [
            {
                "device_id": p.device_id,
                "name": p.name,
                "architecture": p.architecture,
                "capabilities": p.capabilities,
                "firmware": p.firmware,
                "memory_mb": p.memory_mb,
                "cpu_cores": p.cpu_cores,
                "status": p.status,
                "health_score": p.health_score,
                "test_failures_count": p.test_failures_count,
                "avg_response_latency_ms": p.avg_response_latency_ms,
                "is_reserved": p.is_reserved,
                "last_heartbeat": p.last_heartbeat
            } for p in self.farm.values()
        ]
