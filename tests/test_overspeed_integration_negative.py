import csv
import pytest

@pytest.mark.integration
@pytest.mark.overspeed
# Test dirty inputs do not crash the system
def test_dirty_inputs_no_crash(make_monitor, make_sink, tmp_alerts_csv, speed_stream_dirty):
    mon = make_monitor(max_speed=10.0)
    sink = make_sink(tmp_alerts_csv)

    for v in speed_stream_dirty:
        if isinstance(v, (int, float)):
            alerts = mon.on_speed(v)
        else:
            alerts = []
        for a in alerts:
            sink.write(a.kind, a.speed, a.reason)

    rows = list(csv.DictReader(open(tmp_alerts_csv)))
    assert len(rows) == 1
    assert rows[0]["kind"] == "SPEEDING"
    assert float(rows[0]["speed"]) == 20.0
