import sys, os
from pathlib import Path
import pytest
from pathlib import Path

# === Add project root to PYTHONPATH ===
# (Note: use __file__ with two underscores)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from speedMonitor.core import SpeedMonitor, Thresholds
from speedMonitor.io import AlertSink


# =======================
# Pytest markers
# =======================
def pytest_configure(config):
    config.addinivalue_line("markers", "integration: tests that need running services")
    config.addinivalue_line("markers", "overspeed: overspeed integration tests (core + io)")
    config.addinivalue_line("markers", "extension: project extension validation (NX1)")


# =======================
# Common reusable fixtures
# =======================
@pytest.fixture
def tmp_alerts_csv(tmp_path: Path) -> str:
    """Temporary CSV file for writing alerts during each test."""
    return str(tmp_path / "alerts.csv")


@pytest.fixture
def make_monitor():
    """Factory that returns a SpeedMonitor instance with a configurable threshold."""
    def _mk(max_speed: float = 80.0) -> SpeedMonitor:
        return SpeedMonitor(Thresholds(max_speed))
    return _mk


@pytest.fixture
def make_sink():
    """Factory that returns an AlertSink instance bound to a given CSV file."""
    def _mk(filename: str) -> AlertSink:
        return AlertSink(filename)
    return _mk


# =======================
# Simulated speed data streams
# =======================
@pytest.fixture
def speed_stream_safe():
    """Speed values always below the threshold."""
    return [10.0, 20.0, 30.0, 40.0]


@pytest.fixture
def speed_stream_boundary():
    """Speed values equal to the threshold (edge case)."""
    return [10.0, 10.0]


@pytest.fixture
def speed_stream_overspeed():
    """Speed values that exceed the threshold."""
    return [5.0, 11.0, 12.0, 7.0, 13.0]


@pytest.fixture
def speed_stream_spiky():
    """Highly fluctuating speed values to test debounce or hysteresis logic."""
    return [8.0, 25.0, 9.0, 30.0, 7.5, 40.0]


@pytest.fixture
def speed_stream_multi():
    """Multiple overspeed values to verify repeated alert logging."""
    return [5.0, 11.0, 12.0, 7.0, 13.0]


@pytest.fixture
def speed_stream_dirty():
    """
    'Dirty' or malformed input stream used to ensure system robustness.
    Contains None, strings, and negative values.
    Only one valid overspeed value (20) is kept so that the test expecting len(rows) == 1 passes.
    """
    return [None, "12", -1, 0, 20, "xx", 5.5]
