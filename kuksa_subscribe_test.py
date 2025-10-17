from kuksa_client.grpc import VSSClient, VSSClientError

DATABROKER_HOST = 'localhost'
DATABROKER_PORT = 55556
SIGNAL_PATH = 'Vehicle.Speed'

print(f"Attempting to subscribe to {SIGNAL_PATH} at {DATABROKER_HOST}:{DATABROKER_PORT}...")

try:
    # Connect using the simplest constructor that worked for your environment
    with VSSClient(DATABROKER_HOST, DATABROKER_PORT) as client:
        print("Connection successful! Starting subscription stream...")
        
        # FR8: Subscribe to a continuous stream of signal updates
        # We will loop indefinitely to demonstrate a continuous stream
        for i, update in enumerate(client.subscribe_current_values([SIGNAL_PATH])):
            speed_value = update[SIGNAL_PATH].value
            print(f"Update {i+1}: Received new speed value: {speed_value}")
            
            # Stop after 10 updates for a clean demonstration
            if i >= 9:
                break

except VSSClientError as e:
    print(f"\nERROR: A KUKSA Client error occurred. Details: {e.reason}")
except Exception as e:
    print(f"\nERROR: An unexpected error occurred. Details: {e}")

print("\nSubscription test finished.")