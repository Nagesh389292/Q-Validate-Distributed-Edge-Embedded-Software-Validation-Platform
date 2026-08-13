import pytest
import sys
import os

# Add python-validation-engine to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qvalidate.client import DeviceClient
from qvalidate.db import DatabaseManager

@pytest.fixture
def device_client():
    client = DeviceClient(device_id="DEVICE-001")
    client.power_on()
    yield client
    client.clear_fault()

@pytest.fixture
def db_manager():
    return DatabaseManager()
