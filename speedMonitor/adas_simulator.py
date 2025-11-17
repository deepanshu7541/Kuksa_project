import traci
import time
from kuksa_client.grpc import VSSClient, Datapoint

SUMO_BINARY = "sumo"   # or "sumo-gui" if you want visuals
CONFIG_FILE = "sumo_scenarios/simple_highway/sumo_config.sumocfg"
SPEED_SIGNAL = "Vehicle.Speed"
DIST_SIGNAL = "Vehicle.Distance"

def run_sumo_adas(ip="127.0.0.1", port=55556):
    traci.start([SUMO_BINARY, "-c", CONFIG_FILE])

    with VSSClient(ip, port) as client:
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            vehs = traci.vehicle.getIDList()

            if len(vehs) >= 2:
                v1, v2 = vehs[:2]
                speed = traci.vehicle.getSpeed(v1) * 3.6  # m/s → km/h
                pos1 = traci.vehicle.getPosition(v1)[0]
                pos2 = traci.vehicle.getPosition(v2)[0]
                dist = abs(pos2 - pos1)

                print(f"[ADAS] Speed={speed:.2f} km/h, Distance={dist:.2f} m")

                client.set_current_values({
                    SPEED_SIGNAL: Datapoint(speed),
                    DIST_SIGNAL: Datapoint(dist)
                })

                # Safety logic
                if dist < 10:
                    print("[ADAS] 🚨 Too close! Triggering AutoBrake...")
                    from speedMonitor.brake_controller import AutoBrakeSystem
                    AutoBrakeSystem(threshold=20).engage_brake(speed)

            time.sleep(0.5)

    traci.close()