import pytest
import time
from unittest.mock import patch, MagicMock
from speedMonitor.core import monitor_speed


@pytest.mark.extension
@patch("speedMonitor.core.VSSClient")
@patch("speedMonitor.core.AutoBrakeSystem")
def test_auto_brake_triggered_after_hold(mock_brake, mock_client):
    """
    Verifies overspeed persists > hold seconds -> triggers AutoBrakeSystem.engage_brake()
    """
    mock_instance = mock_client.return_value.__enter__.return_value
    mock_instance.get_current_values.side_effect = [
        {"Vehicle.Speed": MagicMock(value=130)},  # overspeed start
        {"Vehicle.Speed": MagicMock(value=130)},  # still overspeed after hold
        {"Vehicle.Speed": MagicMock(value=130)},  # 3rd loop
    ]

    brake_mock = mock_brake.return_value
    brake_mock.active = False

    # Run with small hold and interval for speed
    # Run with small hold and interval for speed
    with patch("time.sleep", return_value=None), patch("time.time", side_effect=[0, 3, 6, 9]):
        monitor_speed(ip="127.0.0.1", port=55556, threshold=120, hold=2, interval=1, max_cycles=3)

    # Check that engage_brake() was invoked
    brake_mock.engage_brake.assert_called()


@pytest.mark.extension
@patch("speedMonitor.core.VSSClient")
@patch("speedMonitor.core.AutoBrakeSystem")
def test_no_brake_when_speed_fluctuates(mock_brake, mock_client):
    """
    Confirms that short or fluctuating overspeed does not trigger brake.
    """
    mock_instance = mock_client.return_value.__enter__.return_value
    mock_instance.get_current_values.side_effect = [
        {"Vehicle.Speed": MagicMock(value=80)},
        {"Vehicle.Speed": MagicMock(value=130)},
        {"Vehicle.Speed": MagicMock(value=90)},  # drops before hold time
        {"Vehicle.Speed": MagicMock(value=70)},
    ]

    brake_mock = mock_brake.return_value
    brake_mock.active = False

    with patch("time.sleep", return_value=None), patch("time.time", side_effect=[0, 1, 1.5, 2, 3]):
        monitor_speed(ip="127.0.0.1", port=55556, threshold=120, hold=2, interval=1)

    brake_mock.engage_brake.assert_not_called()