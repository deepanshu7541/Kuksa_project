import csv, os, sys
from datetime import datetime, timezone

class AlertSink:
    def __init__(self, csv_path:str):
        self.csv_path = csv_path
        new = not os.path.exists(csv_path)
        self._f = open(csv_path, "a", newline="")
        self._w = csv.writer(self._f)
        if new:
            self._w.writerow(["ts", "kind", "value", "reason"])

    def write(self, kind: str, value:float, reason:str):
        ts = datetime.now(timezone.utc).isoformat()
        print(f"[ALERT]{ts} kind={kind} speed={value:.2f} reason={reason}", flush=True)
        self._w.writerow([ts, kind, f"{value:.2f}", reason])
        self._f.flush()

    def close(self):
        try:
            self._f.flush()
            os.fsync(self._.filemo())
        finally:
            self._f.close()

