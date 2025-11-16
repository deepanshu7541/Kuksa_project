

import os
import csv
import math
import time
from pathlib import Path

SUMO_BIN = "/Users/chaomeng/sumo-install/bin/sumo"  #  sumo path

CFG_FILE = "sumo.sumocfg"  
OUT_CSV  = Path("outputs/fcd_traci.csv")
ALERTS_CSV = Path("outputs/alerts.csv")

# ======paras=======
STEP_LENGTH_S = 1.0               
SPEED_LIMIT_KMH = 60.0            
OVERSPEED_TOL_KMH = 5.0          
SLOWDOWN_DURATION_S = 2.0         
MIN_GAP_M = 10.0                 
GAP_HYSTERESIS = 2.0              
LEADER_LOOKAHEAD = 200.0         
ALERT_COOLDOWN_S = 2.0            


last_alert_time = {}  # key=(veh_id, kind) -> sim_time
brake_active = {}     # key=veh_id -> bool

def now_ok_to_alert(veh_id, kind, t):
    k = (veh_id, kind)
    last = last_alert_time.get(k, -1e9)
    if t - last >= ALERT_COOLDOWN_S:
        last_alert_time[k] = t
        return True
    return False

def kmh_to_ms(v):
    return v / 3.6

def ms_to_kmh(v):
    return v * 3.6

def write_alert(writer, t, kind, subject, details):
    writer.writerow([t, kind, subject, details])

def main():
    # export output dir
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    # methods to launch SUMO
    cmd = [SUMO_BIN, "-c", CFG_FILE, "--step-length", str(STEP_LENGTH_S)]

  
    import traci


    traci.start(cmd)

   
    with OUT_CSV.open("w", newline="") as f_fcd, ALERTS_CSV.open("w", newline="") as f_alerts:
        fcd_writer = csv.writer(f_fcd)
        alert_writer = csv.writer(f_alerts)

        fcd_writer.writerow(["time_s", "veh_id", "x_m", "y_m", "speed_kmh"])
        alert_writer.writerow(["time_s", "kind", "subject", "details"])

      
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            t = traci.simulation.getTime()  

            veh_ids = list(traci.vehicle.getIDList())

            for vid in veh_ids:
                x, y = traci.vehicle.getPosition(vid)
                v_ms = traci.vehicle.getSpeed(vid)
                fcd_writer.writerow([t, vid, x, y, ms_to_kmh(v_ms)])


            for vid in veh_ids:
                try:
                    # (leader_id, gap) ; gap = front bumper distance (m)
                    leader = traci.vehicle.getLeader(vid, LEADER_LOOKAHEAD)
                except traci.TraCIException:
                    leader = None

                if not leader:

                    brake_active[vid] = False
                    continue

                leader_id, gap_m = leader

                if gap_m < MIN_GAP_M:
       
                    try:
                        v_leader_ms = traci.vehicle.getSpeed(leader_id)
                    except traci.TraCIException:
                        v_leader_ms = kmh_to_ms(SPEED_LIMIT_KMH)  

                    target_ms = max(0.0, v_leader_ms - 1.0)

                    traci.vehicle.slowDown(vid, target_ms, int(SLOWDOWN_DURATION_S * 1000))
                    if now_ok_to_alert(vid, "DISTANCE_CLOSE", t):
                        write_alert(
                            alert_writer, t, "DISTANCE_CLOSE", vid,
                            f"gap={gap_m:.2f}m < {MIN_GAP_M:.2f}m; target={ms_to_kmh(target_ms):.1f}km/h"
                        )
                    brake_active[vid] = True
                else:

                    if brake_active.get(vid, False) and gap_m > MIN_GAP_M + GAP_HYSTERESIS:
                        if now_ok_to_alert(vid, "DISTANCE_CLEAR", t):
                            write_alert(
                                alert_writer, t, "DISTANCE_CLEAR", vid,
                                f"gap={gap_m:.2f}m >= {MIN_GAP_M + GAP_HYSTERESIS:.2f}m"
                            )
                        brake_active[vid] = False

            for vid in veh_ids:
                v_ms = traci.vehicle.getSpeed(vid)
                v_kmh = ms_to_kmh(v_ms)
                if v_kmh > SPEED_LIMIT_KMH + OVERSPEED_TOL_KMH:
                    target_ms = kmh_to_ms(SPEED_LIMIT_KMH)
                    traci.vehicle.slowDown(vid, target_ms, int(SLOWDOWN_DURATION_S * 1000))
                    if now_ok_to_alert(vid, "OVERSPEED", t):
                        write_alert(
                            alert_writer, t, "OVERSPEED", vid,
                            f"speed={v_kmh:.1f}km/h > limit={SPEED_LIMIT_KMH:.1f}km/h"
                        )

    traci.close()
    print(f"✅ Wrote {OUT_CSV} (via TraCI)")
    print(f"✅ Wrote {ALERTS_CSV} (events)")

if __name__ == "__main__":
    if not Path(SUMO_BIN).exists():
        raise SystemExit(f"SUMO binary not found at: {SUMO_BIN}")
    if not Path("sumo.sumocfg").exists() and not (Path("road.net.xml").exists() and Path("routes.rou.xml").exists()):
        raise SystemExit("Missing sumo.sumocfg or (road.net.xml + routes.rou.xml)")
    main()
