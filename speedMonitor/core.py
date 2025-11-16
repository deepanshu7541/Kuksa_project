import time
from dataclasses import dataclass
from kuksa_client.grpc import VSSClient
from speedMonitor.brake_controller import AutoBrakeSystem

SIG_SPEED = "Vehicle.Speed"


@dataclass
class Alert:
    """Represents a speed alert record used for logging."""
    timestamp: str
    signal: str
    value: float
    threshold: float


class Thresholds:
    """Holds speed thresholds for monitoring."""
    def __init__(self, max_speed: float = 100.0):
        self.max_speed = max_speed


class SpeedMonitor:
    """
    Monitors vehicle speed and triggers the AutoBrake system when overspeed persists.
    """
    def __init__(self, thresholds: Thresholds, hold: float = 2.0, interval: float = 1.0, safe_speed: float = 80.0):
        self.thresholds = thresholds
        self.hold = hold
        self.interval = interval
        self.safe_speed = safe_speed
        self.overspeed_start = None
        self.brake_system = AutoBrakeSystem(threshold=self.thresholds.max_speed, reduction_rate=10)

    def start(self, ip="127.0.0.1", port=55556):
        """Main loop to monitor and control vehicle speed."""
        print(f"[MON] Connecting to Databroker at {ip}:{port}")
        with VSSClient(ip, port) as client:
            print(f"[MON] Connected to Databroker at {ip}:{port}")
            while True:
                try:
                    values = client.get_current_values([SIG_SPEED])
                    speed = getattr(values.get(SIG_SPEED), "value", None)

                    if speed is not None:
                        print(f"[MON] Vehicle.Speed = {speed:.2f}")

                        if speed > self.thresholds.max_speed:
                            if self.overspeed_start is None:
                                self.overspeed_start = time.time()
                            elif (time.time() - self.overspeed_start > self.hold) and not self.brake_system.active:
                                print("[MON] ⚠️ Overspeed persisted! Activating auto brake...")
                                self.brake_system.engage_brake(speed)
                        else:
                            self.overspeed_start = None
                            self.brake_system.active = False
                    else:
                        print("No Vehicle.Speed data available yet.")

                    time.sleep(self.interval)

                except KeyboardInterrupt:
                    print("\n[MON] Monitoring stopped by user.")
                    break
                except Exception as e:
                    print(f"[MON] Error: {e}")
                    time.sleep(2)


# ---- for backward compatibility (so existing demo still works) ----
def monitor_speed(ip="127.0.0.1", port=55556, threshold=120, hold=2, interval=1):
    thresholds = Thresholds(threshold)
    SpeedMonitor(thresholds, hold, interval).start(ip, port)

# import time
# from kuksa_client.grpc import VSSClient
# from speedMonitor.brake_controller import AutoBrakeSystem

# SIG_SPEED = "Vehicle.Speed"

# def monitor_speed(ip="127.0.0.1", port=55556, threshold=120, hold=2, interval=1):
#     with VSSClient(ip, port) as client:
#         print(f"[MON] Connected to Databroker at {ip}:{port}")
#         overspeed_start = None
#         brake_system = AutoBrakeSystem(ip=ip, port=port, threshold=100, reduction_rate=10)

#         while True:
#             try:
#                 values = client.get_current_values([SIG_SPEED])
#                 speed = getattr(values.get(SIG_SPEED), "value", None)

#                 if speed is not None:
#                     print(f"[MON] Vehicle.Speed = {speed:.2f}")

#                     if speed > threshold:
#                         if overspeed_start is None:
#                             overspeed_start = time.time()
#                         elif time.time() - overspeed_start > hold and not brake_system.active:
#                             print("[MON] ⚠️ Overspeed persisted! Activating auto brake...")
#                             brake_system.engage_brake(speed)
#                     else:
#                         overspeed_start = None

#                 else:
#                     print("No Vehicle.Speed data available yet.")

#                 time.sleep(interval)

#             except KeyboardInterrupt:
#                 print("\nMonitoring stopped by user.")
#                 break
#             except Exception as e:
#                 print(f"[MON] Error: {e}")
#                 time.sleep(2)
