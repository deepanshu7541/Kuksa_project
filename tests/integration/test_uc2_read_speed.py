import pytest
from ..utils import read_vss_value

@pytest.mark.integration
def test_read_vehicle_speed(client):
    val = read_vss_value(client, "Vehicle.Speed")
    assert isinstance(val, (int, float))
