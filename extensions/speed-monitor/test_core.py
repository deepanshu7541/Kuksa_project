# Unit tests for SpeedMonitor core logic
# These tests verify that the monitor correctly detects overspeed conditions.
from speedMonitor.core import SpeedMonitor, Thresholds


def test_no_alert_when_below_threshold():
   
   # Verify that no alert is generated when speed is below the threshold.
    m = SpeedMonitor(Thresholds(max_speed=80.0))

    # no alert will return empty list
    assert m.on_speed(79.9) == []

def test_alert_when_above_threshold():

    # Verify that an overspeed alert is generated when speed exceeds the threshold.
    m = SpeedMonitor(Thresholds(max_speed=80.0))
    alerts = m.on_speed(81.0)

    # One alert should be generated
    assert len(alerts) == 1
    assert alerts[0].kind == "overspeed"
