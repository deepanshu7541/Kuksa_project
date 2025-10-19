from dataclasses import dataclass
from typing import List

@dataclass
class Thresholds:
    max_speed:float = 80.0

@dataclass
class Alert:
    kind:str
    speed:float
    reason:str

class SpeedMonitor:
    def __init__(self, th:Thresholds):
        self.th = th

    def on_speed(self,value:float) -> List[Alert]:
       alerts: List[Alert] = []
       if value > self.th.max_speed:
            alerts.append(Alert("overspeed", value, f"Speed {value:.2f} exceeds max {self.th.max_speed:.2f}"))
       return alerts
