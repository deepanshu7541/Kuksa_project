# adas_demo/adas_controller.py
import time
from kuksa_client.grpc import VSSClient

BROKER_IP = "127.0.0.1"
BROKER_PORT = 55556

SIG_SPEED = "Vehicle.Speed"
SIG_DISTANCE = "Vehicle.FrontDistance"
SIG_TARGET = "Vehicle.TargetSpeed"

# parameters
SAFE_DISTANCE = 10.0    # meters
EMERGENCY_DISTANCE = 3.0
MAX_SPEED = 100.0       # km/h
BRAKE_STEP = 15.0       # km/h reduction step
ACCEL_STEP = 5.0        # km/h increase step
INTERVAL = 0.2

def control_loop():
    with VSSClient(BROKER_IP, BROKER_PORT) as client:
        print("[ADAS] Connected to KUKSA Databroker")
        while True:
            try:
                vals = client.get_current_values([SIG_SPEED, SIG_DISTANCE])
                sp_dp = vals.get(SIG_SPEED)
                ds_dp = vals.get(SIG_DISTANCE)

                speed = float(getattr(sp_dp, "value", 0.0) or 0.0)
                dist = getattr(ds_dp, "value", None)

                target = speed
                if dist is not None:
                    if dist <= EMERGENCY_DISTANCE:
                        # emergency brake -> set target to 0
                        target = 0.0
                        print("[ADAS] EMERGENCY BRAKE (dist {:.2f} m)".format(dist))
                    elif dist < SAFE_DISTANCE:
                        # reduce speed proportionally or step down
                        target = max(0.0, speed - BRAKE_STEP)
                        print("[ADAS] Too close (dist {:.2f}). Brake to {:.1f} km/h".format(dist, target))
                    elif dist > SAFE_DISTANCE * 1.5 and speed < MAX_SPEED:
                        target = min(MAX_SPEED, speed + ACCEL_STEP)
                        # gentle acceleration if gap is large
                    else:
                        target = speed
                else:
                    # no distance info: keep speed
                    target = speed

                # write target speed back
                try:
                    client.set_current_values({SIG_TARGET: float(target)})
                except Exception as e:
                    print("[ADAS] KUKSA write error:", e)

            except KeyboardInterrupt:
                print("[ADAS] Stopped by user")
                break
            except Exception as e:
                print("[ADAS] Error reading KUKSA:", e)

            time.sleep(INTERVAL)

if __name__ == "__main__":
    control_loop()