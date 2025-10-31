# tests/test_brake_controller.py
import os
import time
from speedMonitor import brake_controller

def test_brake_event_log(tmp_path):
    csv_path = tmp_path / "brake_events.csv"
    os.chdir(tmp_path)
    brake_controller.log_event("TEST", 100)
    assert csv_path.exists()
    with open(csv_path) as f:
        data = f.read()
    assert "TEST" in data