# tests/test_brake_controller.py
import pytest
from unittest.mock import patch, MagicMock
from speedMonitor.brake_controller import AutoBrakeSystem


@pytest.mark.extension
def test_brake_initialization_defaults():
    brake = AutoBrakeSystem()
    assert brake.ip == "127.0.0.1"
    assert brake.port == 55556
    assert brake.threshold == 100
    assert brake.reduction_rate == 10
    assert not brake.active


@pytest.mark.extension
@patch("speedMonitor.brake_controller.VSSClient")
def test_engage_brake_reduces_speed(mock_client):
    """
    Verifies that engage_brake() keeps reducing Vehicle.Speed 
    until it goes below threshold, and sets Datapoint each step.
    """
    mock_instance = mock_client.return_value.__enter__.return_value
    brake = AutoBrakeSystem(threshold=50, reduction_rate=10)

    brake.engage_brake(current_speed=80)

    # Check multiple calls to Databroker
    assert mock_instance.set_current_values.call_count >= 3
    assert not brake.active  # Reset at the end


@pytest.mark.extension
@patch("speedMonitor.brake_controller.VSSClient")
def test_brake_handles_connection_error(mock_client):
    """
    If VSSClient.set_current_values() throws error, it should print and continue.
    """
    mock_instance = mock_client.return_value.__enter__.return_value
    mock_instance.set_current_values.side_effect = Exception("Network error")

    brake = AutoBrakeSystem(threshold=50, reduction_rate=10)
    brake.engage_brake(current_speed=70)

    # It still reaches the end and resets active flag
    assert not brake.active