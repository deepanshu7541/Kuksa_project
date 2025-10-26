import csv
import pytest

@pytest.mark.integration
@pytest.mark.overspeed
# Test a single overspeed event triggers an alert
def test_multiple_overspeed_events(make_monitor, make_sink, tmp_alerts_csv, speed_stream_multi):
    mon = make_monitor(max_speed=10.0)
    sink = make_sink(tmp_alerts_csv)

    for v in speed_stream_multi:          # [5, 11, 12, 7, 13]
        for a in mon.on_speed(v):
            sink.write(a.kind, a.speed, a.reason)

    rows = list(csv.DictReader(open(tmp_alerts_csv)))
    assert len(rows) == 3
    assert [float(r["speed"]) for r in rows] == [11.0, 12.0, 13.0]
    assert all(r["kind"] == "SPEEDING" for r in rows)
    assert all("exceeds max" in r["reason"] for r in rows)

@pytest.mark.integration
@pytest.mark.overspeed
# Test speeds exactly at the threshold do not trigger alerts
def test_boundary_equals_threshold(make_monitor, make_sink, tmp_alerts_csv, speed_stream_boundary):
    mon = make_monitor(max_speed=10.0)
    sink = make_sink(tmp_alerts_csv)

    for v in speed_stream_boundary:       # [10, 10.0]
        for a in mon.on_speed(v):
            sink.write(a.kind, a.speed, a.reason)

    rows = list(csv.DictReader(open(tmp_alerts_csv)))
    assert len(rows) == 0  # No alerts should be generated
