# speedMonitor/core.py
import time
from kuksa_client.grpc import VSSClient
from speedMonitor.brake_controller import AutoBrakeSystem

<<<<<<< HEAD
# Data structure to hold the monitoring limits (FR6)
@dataclass
class Thresholds:
    max_speed: float = 10.0

# Data structure for reporting anomalies
@dataclass
class Alert:
    kind: str
    speed: float
    reason: str

# Core logic to monitor the speed signal
class SpeedMonitor:
    def __init__(self, th: Thresholds):
        self.th = th

    # Method called for every new speed value (FR7, FR8)
    def on_speed(self, value: float) -> List[Alert]:
        alerts: List[Alert] = []
        
        # Anomaly Detection Logic: Check against the max_speed threshold
        if value > self.th.max_speed:
            alerts.append(Alert("SPEEDING", value, f"Speed {value:.2f} exceeds max {self.th.max_speed:.2f}"))
        
        # FIX: The original code returned [] here. We need to return the alerts list.
        return alerts
=======
SIG_SPEED = "Vehicle.Speed"

def monitor_speed(ip="127.0.0.1", port=55556, threshold=120, hold=2, interval=1):
    with VSSClient(ip, port) as client:
        print(f"[MON] Connected to Databroker at {ip}:{port}")
        overspeed_start = None
        brake_system = AutoBrakeSystem(ip=ip, port=port, threshold=100, reduction_rate=10)

        while True:
            try:
                values = client.get_current_values([SIG_SPEED])
                speed = getattr(values.get(SIG_SPEED), "value", None)

                if speed is not None:
                    print(f"[MON] Vehicle.Speed = {speed:.2f}")

                    # Detect overspeed and trigger brake
                    if speed > threshold:
                        if overspeed_start is None:
                            overspeed_start = time.time()
                        elif time.time() - overspeed_start > hold and not brake_system.active:
                            print("[MON] ⚠️ Overspeed persisted! Activating auto brake...")
                            brake_system.engage_brake(speed)
                    else:
                        overspeed_start = None

                else:
                    print("[MON] No Vehicle.Speed data available yet.")

                time.sleep(interval)

            except KeyboardInterrupt:
                print("\n[MON] Monitoring stopped by user.")
                break
            except Exception as e:
                print(f"[MON] Error: {e}")
                time.sleep(2)

# from dataclasses import dataclass
# from typing import List

# @dataclass
# class Thresholds:
#     max_speed: float = 80.0

# @dataclass
# class Alert:
#     kind: str
#     speed: float
#     reason: str

# class SpeedMonitor:
#     def __init__(self, th: Thresholds):
#         self.th = th

#     def on_speed(self, value: float) -> List[Alert]:
#         alerts: List[Alert] = []
        
#         if value > self.th.max_speed:
#             alerts.append(Alert("SPEEDING", value, f"Speed {value:.2f} exceeds max {self.th.max_speed:.2f}"))
        
#         return alerts
>>>>>>> a9a1de6 (Auto-braking system update)
