
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


from speedMonitor.core import SpeedMonitor, Thresholds
from speedMonitor.io import AlertSink

import pytest
from pathlib import Path

def pytest_configure(config):
    # Register custom markers
    config.addinivalue_line("markers", "extension: project extension validation (NX1)")
    config.addinivalue_line("markers", "integration: integration test suite")
    config.addinivalue_line("markers", "overspeed: overspeed integration tests (core + io)")

# ===== Fixtures =====
@pytest.fixture
def tmp_alerts_csv(tmp_path: Path) -> str:
    return str(tmp_path / "alerts.csv")

@pytest.fixture
def make_monitor():
    def _mk(max_speed=10.0):
        return SpeedMonitor(Thresholds(max_speed))
    return _mk

@pytest.fixture
def make_sink():
    def _mk(filename: str):
        return AlertSink(filename)
    return _mk

@pytest.fixture
def speed_stream_multi():     return [5.0, 11.0, 12.0, 7.0, 13.0]

@pytest.fixture
def speed_stream_boundary():  return [10.0, 10.0]

@pytest.fixture
def speed_stream_dirty():
    # only 20.0 should trigger; others are invalid or below threshold
    return [None, "12", -1, 20]
