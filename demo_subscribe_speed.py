import time
from kuksa_client.grpc import VSSClient

MAX_UPDATES = 10  

if __name__ == "__main__":
    c = VSSClient("127.0.0.1", 55556); c.connect()
    print(f"Subscribed to Vehicle.Speed (print {MAX_UPDATES} updates then exit)...")

    sub = c.subscribe_current_values(["Vehicle.Speed"])
    count = 0
    try:
        for update in sub:
            if "Vehicle.Speed" in update:
                val = update["Vehicle.Speed"].value
                print(f"Speed updated: {val:.2f} km/h")
                count += 1
                if count >= MAX_UPDATES:
                    break
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
      
        if hasattr(c, "disconnect"):
            c.disconnect()
        elif hasattr(c, "close"):
            c.close()
