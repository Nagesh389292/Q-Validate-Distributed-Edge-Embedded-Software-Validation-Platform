import subprocess
import json
import time
import os
from typing import List, Tuple
from qvalidate.models import DeviceStatus, DeviceState, MetricSample

class DeviceClient:
    """
    Client for managing and communicating with C++ Simulated Edge Devices.
    Supports both direct C++ binary IPC / emulation and gRPC interfaces.
    """
    def __init__(self, device_id: str = "DEVICE-001", binary_path: str = None):
        self.device_id = device_id
        if binary_path is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            self.binary_path = os.path.join(base_dir, "build", "Release", "qvalidate_device_runtime.exe")
        else:
            self.binary_path = binary_path
        
        # Internal state tracking for Python simulator interface
        self._state = DeviceState.POWERED_OFF
        self._firmware_version = "4.2.1"
        self._build_id = "BUILD-1042"
        self._cpu_usage = 14.2
        self._memory_used_mb = 1024.0
        self._memory_total_mb = 8192.0
        self._temp_celsius = 42.0
        self._active_fault = "NONE"
        self._boot_time = time.time()

    def get_status(self) -> DeviceStatus:
        uptime = time.time() - self._boot_time if self._state == DeviceState.READY else 0.0
        is_healthy = self._state == DeviceState.READY and self._active_fault == "NONE"
        return DeviceStatus(
            device_id=self.device_id,
            state=self._state,
            firmware_version=self._firmware_version,
            uptime_seconds=round(uptime, 2),
            cpu_usage_pct=round(self._cpu_usage, 2),
            memory_used_mb=round(self._memory_used_mb, 2),
            memory_total_mb=self._memory_total_mb,
            temperature_celsius=round(self._temp_celsius, 2),
            is_healthy=is_healthy,
            active_fault=self._active_fault
        )

    def power_on(self) -> Tuple[bool, float, str]:
        start = time.time()
        self._state = DeviceState.BOOTING
        time.sleep(0.1)
        self._state = DeviceState.INITIALIZING
        time.sleep(0.05)
        
        if self._active_fault == "CORRUPTED_FIRMWARE":
            self._state = DeviceState.ERROR
            return False, round(time.time() - start, 3), "Boot failed: Corrupted firmware image"
            
        self._state = DeviceState.READY
        self._boot_time = time.time()
        dur = round(time.time() - start, 3)
        return True, dur, f"Device {self.device_id} powered on successfully in {dur}s"

    def reset(self, hard_reset: bool = False) -> Tuple[bool, float, str]:
        start = time.time()
        self._state = DeviceState.POWERED_OFF
        ok, boot_dur, msg = self.power_on()
        total_dur = round(time.time() - start, 3)
        return ok, total_dur, f"Reset complete. {msg}"

    def deploy_build(self, build_id: str, version: str) -> Tuple[bool, float, str]:
        start = time.time()
        time.sleep(0.15)
        self._build_id = build_id
        self._firmware_version = version
        ok, reset_dur, msg = self.reset()
        total_dur = round(time.time() - start, 3)
        return ok, total_dur, f"Build {build_id} ({version}) deployed successfully in {total_dur}s"

    def inject_fault(self, fault_type: str, intensity: float = 90.0) -> Tuple[bool, str]:
        self._active_fault = fault_type
        if fault_type == "CPU_OVERLOAD":
            self._cpu_usage = min(100.0, max(85.0, intensity))
            self._temp_celsius = 82.5
            self._state = DeviceState.DEGRADED
        elif fault_type == "MEMORY_PRESSURE":
            self._memory_used_mb = min(self._memory_total_mb, max(7500.0, intensity))
            self._state = DeviceState.DEGRADED
        elif fault_type == "CORRUPTED_FIRMWARE":
            self._state = DeviceState.ERROR
        elif fault_type == "PROCESS_CRASH":
            self._state = DeviceState.ERROR
        return True, f"Fault {fault_type} injected into {self.device_id}"

    def clear_fault(self) -> Tuple[bool, str]:
        self._active_fault = "NONE"
        self._cpu_usage = 15.0
        self._memory_used_mb = 1024.0
        self._temp_celsius = 42.0
        self._state = DeviceState.READY
        return True, f"Fault cleared on {self.device_id}"

    def collect_metrics(self, count: int = 5) -> List[MetricSample]:
        samples = []
        now = time.time()
        for i in range(count):
            samples.append(MetricSample(
                timestamp=now + (i * 0.1),
                cpu_pct=self._cpu_usage,
                memory_mb=self._memory_used_mb,
                temp_celsius=self._temp_celsius
            ))
        return samples

    def run_cxx_native_verification(self) -> subprocess.CompletedProcess:
        """Invokes the native C++ binary to verify native binary execution."""
        if os.path.exists(self.binary_path):
            return subprocess.run([self.binary_path], capture_output=True, text=True, check=True)
        else:
            raise FileNotFoundError(f"C++ Binary not found at {self.binary_path}")
