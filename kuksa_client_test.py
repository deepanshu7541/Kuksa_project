from kuksa_client.grpc import VSSClient, VSSClientError

# The Data Broker is accessible on localhost:55556 (external port)
DATABROKER_HOST = 'localhost'
DATABROKER_PORT = 55556

print(f"Attempting to connect to {DATABROKER_HOST}:{DATABROKER_PORT}...")

try:
    # --- The Fix: Use the simplest constructor ---
    # Your version of the client library uses an insecure connection by default.
    with VSSClient(DATABROKER_HOST, DATABROKER_PORT) as client:
        print("Connection successful! Fetching data...")

        # 1. Get the current value of a signal
        speed_value = client.get_current_values(['Vehicle.Speed'])
        
        # 2. Print the result
        print(f"\n--- CURRENT VALUE ---")
        # Ensure we access the value correctly (assuming it returns a dict with Signal objects)
        print(f"Vehicle Speed: {speed_value['Vehicle.Speed'].value}")
        
        # 3. Subscribe to get a continuous stream 
        print("\n--- SUBSCRIPTION (5 Updates) ---")
        print("Waiting for updates from Mock Provider...")
        for i, update in enumerate(client.subscribe(['Vehicle.Speed'], count=5)):
            print(f"Update {i+1}: Vehicle Speed = {update['Vehicle.Speed'].value}")

except VSSClientError as e:
    print(f"\nERROR: A KUKSA Client error occurred.")
    print(f"Details: {e.reason}")
except Exception as e:
    # We kept the generic exception for any remaining quirks
    print(f"\nERROR: An unexpected error occurred.")
    print(f"Details: {e}")

print("\nClient script finished. The KUKSA system is running locally. 🎉")