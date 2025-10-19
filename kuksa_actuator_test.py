from kuksa_client.grpc import VSSClient, Datapoint

DATABROKER_HOST = 'localhost'
DATABROKER_PORT = 55556
ACTUATOR_PATH = 'Vehicle.Body.Windshield.Front.Wiping.System.TargetPosition'

print(f"--- Testing Actuator: Setting {ACTUATOR_PATH} ---")

try:
    with VSSClient(DATABROKER_HOST, DATABROKER_PORT) as client:
        # Define the new value to set (e.g., target position 50)
        new_value = 50
        
        print(f"Attempting to SET value to: {new_value}")
        
        # Set the current value for the actuator
        client.set_current_values({
            ACTUATOR_PATH: Datapoint(new_value)
        })
        print(f"✅ SET successful.")
        
        # Read the value back to confirm the write operation
        read_values = client.get_current_values([ACTUATOR_PATH])
        confirmed_value = read_values[ACTUATOR_PATH].value
        
        print(f"✅ CONFIRMED: Readback value is: {confirmed_value}")
        
        if confirmed_value == new_value:
             print("\nFunctionality demonstrated: The client can control an actuator.")
        else:
             print("\n❌ FAIL: Value was set but readback was incorrect.")
             
except Exception as e:
    print(f"\nERROR during actuator test: {e}")