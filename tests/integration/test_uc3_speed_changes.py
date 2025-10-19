import time
import pytest
from ..utils import read_vss_value

@pytest.mark.integration
def test_vehicle_speed_changes_over_time(client):
    v1 = read_vss_value(client, "Vehicle.Speed")
    assert isinstance(v1, (int, float))
    changed = False
    deadline = time.time() + 5.0
    while time.time() < deadline:
        time.sleep(0.5)
        v2 = read_vss_value(client, "Vehicle.Speed")
        if isinstance(v2, (int, float)) and v2 != v1:
            changed = True
            break
    assert changed


