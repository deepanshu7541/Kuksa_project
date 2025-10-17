import pytest
from kuksa_client.grpc import VSSClient

@pytest.mark.integration
def test_vehicle_speed_available():
    """Verifies Vehicle.Speed is available and non-negative (Base F2 check)."""
    client = VSSClient('127.0.0.1', 55556)
    client.connect()
    
    try:
        value = client.get_current_values(['Vehicle.Speed'])['Vehicle.Speed'].value
    except Exception as e:
        pytest.fail(f"Could not read Vehicle.Speed: {e}")

    assert value is not None
    assert value >= 0