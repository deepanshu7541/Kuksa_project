# adas_csv/replay_gap_to_kuksa.py
import csv
import time
import sys
from decide import decide_target  # reuse your decide logic (put a copy under adas_csv or adjust import)
try:
    from kuksa_client.grpc import VSSClient
    KUKSA_AVAILABLE = True
except Exception:
    KUKSA_AVAILABLE = False

BROKER_IP = "127.0.0.1"
BROKER_PORT = 55556
# SIG_SPEED     = "Vehicle.Speed"
# SIG_DISTANCE  = "Vehicle.ADAS.DistanceToLead"
# SIG_TARGET    = "Vehicle.ADAS.TargetSpeed"
SIG_SPEED    = "Vehicle.Speed"
SIG_DISTANCE = "Vehicle.CurrentLocation.Longitude"   # placeholder for distance
SIG_TARGET   = "Vehicle.Acceleration.Longitudinal"   # placeholder for target


def replay(gap_csv, publish_to_kuksa=False, step_s=0.1):
    if publish_to_kuksa and not KUKSA_AVAILABLE:
        print("kuksa-client not available; set publish_to_kuksa=False or install kuksa-client")
        publish_to_kuksa = False

    client = None
    if publish_to_kuksa:
        client = VSSClient(BROKER_IP, BROKER_PORT)

    if publish_to_kuksa:
        client.__enter__()

    with open(gap_csv, newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            t = float(r["time_s"])
            ego_speed = float(r["ego_speed"]) if r["ego_speed"] else 0.0
            dist = float(r["distance_m"]) if r["distance_m"] else None

            target, action = decide_target(ego_speed, dist)
            print(f"[REPLAY] t={t:.2f} ego_sp={ego_speed:.1f} dist={dist} -> target={target:.1f} action={action}")

            if publish_to_kuksa:
                payload = {SIG_SPEED: float(ego_speed)}
                if dist is not None:
                    payload[SIG_DISTANCE] = float(dist)
                # write current speed & distance
                client.set_current_values(payload)
                # write controller target
                client.set_current_values({SIG_TARGET: float(target)})

            time.sleep(step_s)

    if publish_to_kuksa:
        client.__exit__(None, None, None)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: replay_gap_to_kuksa.py gap.csv [publish_to_kuksa True/False]")
        sys.exit(1)
    gap = sys.argv[1]
    pub = (len(sys.argv) >= 3 and sys.argv[2].lower() == "true")
    replay(gap, publish_to_kuksa=pub)