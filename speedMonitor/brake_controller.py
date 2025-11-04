import time
from kuksa_client.grpc import VSSClient, Datapoint

SPEED_SIGNAL = "Vehicle.Speed"

class AutoBrakeSystem:
    def __init__(self, ip="127.0.0.1", port=55556, threshold=100, reduction_rate=10):
        """
        AutoBrakeSystem simulates an automatic braking system that 
        slows the vehicle to a safe speed when overspeed is detected.
        """
        self.ip = ip
        self.port = port
        self.threshold = threshold
        self.reduction_rate = reduction_rate
        self.active = False

    def engage_brake(self, current_speed):
        print(f"[BRAKE] ⚠️ Overspeed detected: {current_speed:.2f} km/h")
        self.active = True

        with VSSClient(self.ip, self.port) as client:
            while current_speed > self.threshold:
                current_speed -= self.reduction_rate
                if current_speed < 0:
                    current_speed = 0

                try:
                    client.set_current_values({SPEED_SIGNAL: Datapoint(current_speed)})
                    print(f"[BRAKE] Applying brakes... Speed = {current_speed:.2f}")
                except Exception as e:
                    print(f"[BRAKE] Error setting speed: {e}")
                time.sleep(1)

        print("[BRAKE] Vehicle speed normalized.")
        self.active = False