from qvalidate.client import DeviceClient
from qvalidate.models import DeviceState

def test_corrupted_firmware_fault(device_client: DeviceClient):
    """
    FAULT-005: Inject corrupted firmware fault and verify device enters ERROR state on reboot.
    """
    device_client.inject_fault("CORRUPTED_FIRMWARE")
    ok, dur, msg = device_client.power_on()
    assert ok is False, "Corrupted firmware reboot must fail"
    status = device_client.get_status()
    assert status.state == DeviceState.ERROR, f"Expected ERROR state, got {status.state}"

    # Clear fault and recover
    device_client.clear_fault()
    ok_rec, dur_rec, msg_rec = device_client.power_on()
    assert ok_rec is True, "Device should boot cleanly after clearing firmware fault"
