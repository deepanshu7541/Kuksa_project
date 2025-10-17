from time import sleep
from kuksa_client.grpc import VSSClient

DATABROKER_ADDR = '127.0.0.1'
DATABROKER_PORT = 55556
SPEED_SIGNAL = 'Vehicle.Speed'

def read_and_verify_speed():
    """Connects, reads speed twice, and checks for dynamic change."""
    print(f"Connecting to Databroker at {DATABROKER_ADDR}:{DATABROKER_PORT}")
    try:
        # Note: kuksa-client v0.5.0 uses standard VSSClient connection methods
        c = VSSClient(DATABROKER_ADDR, DATABROKER_PORT)
        c.connect()
    except Exception as e:
        print(f"ERROR: Failed to connect to Databroker. Is Docker running? {e}")
        return

    # Read v1
    v1 = c.get_current_values([SPEED_SIGNAL])[SPEED_SIGNAL].value
    sleep(1.0) 

    # Read v2
    v2 = c.get_current_values([SPEED_SIGNAL])[SPEED_SIGNAL].value

    print("--- Signal Read Results ---")
    print(f"{SPEED_SIGNAL} v1: {v1}")
    print(f"{SPEED_SIGNAL} v2: {v2}")

    if v1 != v2:
        print("\n✅ Verification Successful: Signal is dynamic (F2 demonstrated).")
    else:
        print("\n❌ Verification Failed: Signal value did not change.")
    
if __name__ == "__main__":
    read_and_verify_speed()