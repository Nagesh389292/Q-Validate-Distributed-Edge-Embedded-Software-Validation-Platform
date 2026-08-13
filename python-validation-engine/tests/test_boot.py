from qvalidate.client import DeviceClient
from qvalidate.models import DeviceState

def test_device_boot_sequence(device_client: DeviceClient):
    """
    BOOT-001: Verify device power on and boot state machine transitions to READY.
    """
    device_client.reset(hard_reset=True)
    status = device_client.get_status()
    assert status.state == DeviceState.READY, f"Expected READY, got {status.state}"
    assert status.firmware_version == "4.2.1", f"Unexpected firmware: {status.firmware_version}"
    assert status.is_healthy is True, "Device should be healthy upon boot"

def test_firmware_deploy_and_reboot(device_client: DeviceClient):
    """
    BOOT-002: Verify deploying new firmware image and auto-reboot.
    """
    ok, duration, msg = device_client.deploy_build("BUILD-1043", "4.2.2")
    assert ok is True, f"Deploy failed: {msg}"
    status = device_client.get_status()
    assert status.firmware_version == "4.2.2", f"Firmware version expected 4.2.2, got {status.firmware_version}"
    assert status.state == DeviceState.READY, "Device state must be READY after firmware update"
