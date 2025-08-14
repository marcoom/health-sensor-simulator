import pytest
from fastapi.testclient import TestClient
from health_sensor_simulator.main import app

@pytest.fixture
def test_client():
    test_client = TestClient(app)
    return test_client


