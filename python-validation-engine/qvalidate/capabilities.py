from typing import List, Dict, Set

class HardwareCapability:
    CPU = "CPU"
    MEMORY = "MEMORY"
    DSP = "DSP"
    AI_ACCELERATOR = "AI_ACCELERATOR"
    NETWORK = "NETWORK"

DEVICE_FARM_CAPABILITIES: Dict[str, List[str]] = {
    "DEVICE-001": ["CPU", "MEMORY", "AI_ACCELERATOR"],
    "DEVICE-002": ["CPU", "MEMORY", "DSP"],
    "DEVICE-003": ["CPU", "MEMORY", "NETWORK"],
    "DEVICE-004": ["CPU", "MEMORY", "DSP", "AI_ACCELERATOR"],
    "DEVICE-005": ["CPU", "MEMORY", "AI_ACCELERATOR"],
    "DEVICE-006": ["CPU", "MEMORY", "DSP"],
    "DEVICE-007": ["CPU", "MEMORY", "NETWORK"],
    "DEVICE-008": ["CPU", "MEMORY", "DSP", "AI_ACCELERATOR"],
    "DEVICE-009": ["CPU", "MEMORY", "AI_ACCELERATOR"],
    "DEVICE-010": ["CPU", "MEMORY", "DSP", "NETWORK"]
}

def is_device_capable(device_capabilities: List[str], required_capability: str) -> bool:
    """Returns True if the target device supports the required hardware capability."""
    if not required_capability or required_capability == "CPU" or required_capability == "MEMORY":
        return True
    return required_capability in device_capabilities
