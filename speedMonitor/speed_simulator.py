import time
import random
from kuksa_client.grpc import VSSClient, Datapoint

SPEED_SIGNAL = "Vehicle.Speed"

def main(ip="127.0.0.1", port=55556):
    print("🚗 Starting Vehicle.Speed simulator...")

    with VSSClient(ip, port) as client:
        while True:
            try:
                speed = random.uniform(50, 150)  # Simulate speed between 50–150 km/h
                client.set_current_values({SPEED_SIGNAL: Datapoint(speed)})
                print(f"[SIM] Set Vehicle.Speed = {speed:.2f} km/h")
                time.sleep(2)
            except KeyboardInterrupt:
                print("\n[SIM] Simulator stopped.")
                break
            except Exception as e:
                print(f"[SIM] Error: {e}")
                time.sleep(2)

if __name__ == "__main__":
    main()