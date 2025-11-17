import csv
import sys
from collections import defaultdict
from pathlib import Path

def compute_gap(input_csv, ego_id="ego", lead_id="lead", start=None, end=None, out_csv="gap.csv"):
    times = defaultdict(dict)  # times[time_s][veh_id] = row
    with open(input_csv, newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            t = float(r["time_s"])
            vid = r["veh_id"]
            if start is not None and t < float(start): continue
            if end is not None and t > float(end): continue
            times[t][vid] = r

    times_sorted = sorted(times.items(), key=lambda x: x[0])
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time_s","ego_id","lead_id","ego_speed","lead_speed","distance_m"])
        for t, rowmap in times_sorted:
            ego = rowmap.get(ego_id)
            lead = rowmap.get(lead_id)
            if ego and lead:
                # compute distance along x-axis (assumes same lane/edge direction). If not appropriate use euclidean.
                try:
                    distance = float(lead["x"]) - float(ego["x"])
                except Exception:
                    # fallback to Euclidean
                    import math
                    dx = float(lead["x"]) - float(ego["x"])
                    dy = float(lead["y"]) - float(ego["y"])
                    distance = math.hypot(dx, dy)
                w.writerow([t, ego_id, lead_id, ego.get("speed",""), lead.get("speed",""), max(0.0, distance)])
            elif ego and not lead:
                w.writerow([t, ego_id, lead_id, ego.get("speed",""), "", ""])
    print(f"Wrote {out_csv}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: compute_gap.py fcd.csv ego_id lead_id [start] [end] [out_csv]")
        sys.exit(1)
    input_csv = sys.argv[1]
    ego = sys.argv[2]
    lead = sys.argv[3]
    start = sys.argv[4] if len(sys.argv) >= 5 else None
    end = sys.argv[5] if len(sys.argv) >= 6 else None
    out = sys.argv[6] if len(sys.argv) >= 7 else "gap.csv"
    compute_gap(input_csv, ego, lead, start, end, out)