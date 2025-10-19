from dataclasses import dataclass
from typing import List

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