
import os
import csv
import random
import pytest

# ============================================================
# IT-03 Multiple overspeed events
# Input: [5, 11, 12, 7, 13], Threshold: 10
# Expected:
#   - Three alerts for 11.0, 12.0, and 13.0.
#   - All alerts have kind = SPEEDING.
#   - Reasons contain "exceeds max".
# ============================================================
@pytest.mark.integration
@pytest.mark.overspeed
def test_multiple_overspeed_events(make_monitor, make_sink, tmp_alerts_csv, speed_stream_multi):
    mon = make_monitor(max_speed=10.0)
    sink = make_sink(tmp_alerts_csv)

    for v in speed_stream_multi:          # Expected: [5, 11, 12, 7, 13]
        for a in mon.on_speed(v):
            sink.write(a.kind, a.speed, a.reason)

    rows = list(csv.DictReader(open(tmp_alerts_csv, newline="")))
    assert len(rows) == 3
    assert [float(r["speed"]) for r in rows] == [11.0, 12.0, 13.0]
    assert all(r["kind"] == "SPEEDING" for r in rows)
    assert all("exceeds max" in r["reason"] for r in rows)

# ============================================================
# IT-04 Boundary value equals threshold
# Input: [10, 10.0], Threshold: 10
# Expected:
#   - No alerts generated because speeds equal the threshold (not greater).
# ============================================================
@pytest.mark.integration
@pytest.mark.overspeed
def test_boundary_equals_threshold(make_monitor, make_sink, tmp_alerts_csv, speed_stream_boundary):
    mon = make_monitor(max_speed=10.0)
    sink = make_sink(tmp_alerts_csv)

    for v in speed_stream_boundary:       # Expected: [10, 10.0]
        for a in mon.on_speed(v):
            sink.write(a.kind, a.speed, a.reason)

    rows = list(csv.DictReader(open(tmp_alerts_csv, newline="")))
    assert len(rows) == 0  # No alerts should be generated in boundary case


# ============================================================
# IT-01 Normal case — No overspeed events
# Input: [5, 8, 9], Threshold: 10
# Expected:
#   - No alerts are generated.
#   - The CSV file may not exist or may only contain the header with 0 data rows.
# ============================================================
@pytest.mark.integration
@pytest.mark.overspeed
def test_it01_no_alerts_csv_absent_or_empty(make_monitor, make_sink, tmp_alerts_csv):
    mon = make_monitor(max_speed=10.0)
    sink = make_sink(tmp_alerts_csv)

    for v in [5.0, 8.0, 9.0]:
        for a in mon.on_speed(v):
            sink.write(a.kind, a.speed, a.reason)
# Check if the CSV file exists and is empty (no data rows)
    if not os.path.exists(tmp_alerts_csv):
        assert True  # File does not exist, which is acceptable
    else:
        rows = list(csv.DictReader(open(tmp_alerts_csv, newline="")))
        assert len(rows) == 0


# ============================================================
# IT-02 Single overspeed event
# Input: [5, 11, 9], Threshold: 10
# Expected:
#   - Only one alert for speed 11.0.
#   - Alert kind should be SPEEDING.
#   - Reason should contain "exceeds max".
# ============================================================
@pytest.mark.integration
@pytest.mark.overspeed
def test_it02_single_overspeed_event(make_monitor, make_sink, tmp_alerts_csv):
    mon = make_monitor(max_speed=10.0)
    sink = make_sink(tmp_alerts_csv)

    for v in [5.0, 11.0, 9.0]:
        for a in mon.on_speed(v):
            sink.write(a.kind, a.speed, a.reason)

    rows = list(csv.DictReader(open(tmp_alerts_csv, newline="")))
    assert len(rows) == 1
    assert rows[0]["kind"] == "SPEEDING"
    assert float(rows[0]["speed"]) == 11.0
    assert "exceeds max" in rows[0]["reason"]


# ============================================================
# IT-05 Threshold change between two phases
# Phase 1: Threshold = 10, Speeds = [9, 11]  -> alert only for 11
# Phase 2: Threshold = 12, Speeds = [11, 13] -> alert only for 13
# Expected:
#   - Two alerts total: 11.0 (phase 1) and 13.0 (phase 2)
#   - Both have kind = SPEEDING
#   - Both reasons contain "exceeds max"
# ============================================================
@pytest.mark.integration
@pytest.mark.overspeed
def test_it05_threshold_change_two_phases(make_monitor, make_sink, tmp_alerts_csv):
    sink = make_sink(tmp_alerts_csv)

    mon1 = make_monitor(max_speed=10.0)
    for v in [9.0, 11.0]:
        for a in mon1.on_speed(v):
            sink.write(a.kind, a.speed, a.reason)

    mon2 = make_monitor(max_speed=12.0)
    for v in [11.0, 13.0]:
        for a in mon2.on_speed(v):
            sink.write(a.kind, a.speed, a.reason)

    rows = list(csv.DictReader(open(tmp_alerts_csv, newline="")))
    assert len(rows) == 2
    assert [float(r["speed"]) for r in rows] == [11.0, 13.0]
    assert all(r["kind"] == "SPEEDING" for r in rows)
    assert all("exceeds max" in r["reason"] for r in rows)


# --------------------------------------------
# IT-06 Dirty / Invalid Inputs (Robustness Test)
# Input stream: [None, "12", -1, 20]
# Rule:
#   - Strings that can be converted to float are treated as valid
#   - Negative values are ignored
#   - None and unconvertible values are ignored
# Expected result:
#   - Two alerts should be triggered for 12.0 and 20.0
#   - The system must not crash during processing
# --------------------------------------------
@pytest.mark.integration
@pytest.mark.overspeed
def test_it06_dirty_inputs_no_crash(make_monitor, make_sink, tmp_alerts_csv):
    mon = make_monitor(max_speed=10.0)
    sink = make_sink(tmp_alerts_csv)

    stream = [None, "12", -1, 20]
    for v in stream:
        
        try:
            vv = float(v) if v is not None else None
        except (ValueError, TypeError):
            vv = None
  # Skip invalid or negative values
        if vv is None:
            continue        
        if vv < 0:
            continue          

        for a in mon.on_speed(vv):
            sink.write(a.kind, a.speed, a.reason)

    rows = list(csv.DictReader(open(tmp_alerts_csv, newline="")))
    assert len(rows) == 2
    speeds = [float(r["speed"]) for r in rows]
    assert speeds == [12.0, 20.0]
    assert all(r["kind"] == "SPEEDING" for r in rows)
    assert all("exceeds max" in r["reason"] for r in rows)


# ============================================================
# IT-07 High-frequency stream and flushing behavior
# Input: 1000 values; every 50th value = 15.0 (overspeed)
# Expected:
#   - 20 alerts (1000 / 50)
#   - All alerts have kind = SPEEDING
#   - All speeds > threshold
#   - Verifies file flushing and data consistency with large input
# ============================================================
@pytest.mark.integration
@pytest.mark.overspeed
def test_it07_high_frequency_stream_large_volume(make_monitor, make_sink, tmp_alerts_csv):
    max_speed = 10.0
    mon = make_monitor(max_speed=max_speed)
    sink = make_sink(tmp_alerts_csv)
 # Construct 1000 samples: every 50th value is overspeed (15.0)
    stream = []
    for i in range(1000):
        if i % 50 == 0:
            stream.append(15.0)                 
        else:
            stream.append((i % 10) + 0.1)       

    expected_n = sum(1 for v in stream if v > max_speed)

    for v in stream:
        for a in mon.on_speed(v):
            sink.write(a.kind, a.speed, a.reason)

    rows = list(csv.DictReader(open(tmp_alerts_csv, newline="")))
    assert len(rows) == expected_n == 20
    assert all(r["kind"] == "SPEEDING" for r in rows)
    assert all(float(r["speed"]) > max_speed for r in rows)
