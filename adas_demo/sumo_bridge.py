# adas_demo/sumo_bridge.py
import os, time, sys
import traci
from kuksa_client.grpc import VSSClient

# Signals used between bridge and ADAS controller / your existing code
SIG_SPEED = "Vehicle.Speed"        # reported speed in km/h
SIG_DISTANCE = "Vehicle.FrontDistance"  # meters
SIG_TARGET = "Vehicle.TargetSpeed" # km/h -> desired speed from ADAS

# SUMO config (relative to project)
HERE = os.path.dirname(__file__)
SUMO_CFG = os.path.abspath(os.path.join(HERE, "../adas_demo/simple.sumocfg"))

# choose "sumo" or "sumo-gui"
SUMO_BIN = "sumo"   # change to "sumo-gui" if you want GUI

BROKER_IP = "127.0.0.1"
BROKER_PORT = 55556

def run_bridge():
    print("[BRIDGE] Starting SUMO with:", SUMO_CFG)
    traci.start([SUMO_BIN, "-c", SUMO_CFG])
    print("[BRIDGE] SUMO started (TraCI connected)")

    with VSSClient(BROKER_IP, BROKER_PORT) as client:
        print("[BRIDGE] Connected to KUKSA Databroker")
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            vehs = traci.vehicle.getIDList()

            if not vehs:
                time.sleep(0.05)
                continue

            # select follower vehicle (our controlled vehicle)
            vid = "follower" if "follower" in vehs else vehs[0]

            # get speed (m/s -> km/h)
            speed_kmh = traci.vehicle.getSpeed(vid) * 3.6

            # compute distance to leader if present
            distance = None
            if "leader" in vehs and vid == "follower":
                lead_pos = traci.vehicle.getDistance("leader")
                fol_pos = traci.vehicle.getDistance("follower")
                # leader ahead will have larger distance value on same edge -> approximate
                distance = max(0.0, lead_pos - fol_pos)

            # write to KUKSA
            try:
                data = {SIG_SPEED: speed_kmh}
                if distance is not None:
                    data[SIG_DISTANCE] = distance
                client.set_current_values(data)
            except Exception as e:
                print("[BRIDGE] KUKSA write error:", e)

            # read target from KUKSA (if ADAS controller wrote it)
            try:
                vals = client.get_current_values([SIG_TARGET])
                tdp = vals.get(SIG_TARGET)
                target = getattr(tdp, "value", None)
                if target is not None:
                    # apply to SUMO: convert km/h -> m/s
                    traci.vehicle.setSpeed(vid, float(target) / 3.6)
            except Exception as e:
                # ignore read errors (may be not yet set)
                pass

            # debug print
            print(f"[BRIDGE] {vid} speed={speed_kmh:.1f} km/h dist={distance}")

            time.sleep(0.1)

    traci.close()

if __name__ == "__main__":
    run_bridge()