from kuksa_client.grpc import VSSClient
import sys # Import the system module

DATABROKER_HOST = 'localhost'
DATABROKER_PORT = 55556
SIGNAL_PATH = 'Vehicle.Speed'

print(f"--- Verifying Metadata for {SIGNAL_PATH} ---")

try:
    with VSSClient(DATABROKER_HOST, DATABROKER_PORT) as client:
        
        metadata_dict = client.get_metadata([SIGNAL_PATH])
        
        if not metadata_dict or SIGNAL_PATH not in metadata_dict:
            print(f"ERROR: Metadata not found for {SIGNAL_PATH}.")
            # FIX: Use sys.exit() to stop execution immediately
            sys.exit(1)

        metadata = metadata_dict[SIGNAL_PATH]
        
        expected_type = 'FLOAT'
        expected_unit = 'km/h' 

        print(f"Data Type: {metadata.data_type}")
        print(f"Unit: {metadata.unit}")
        
        if metadata.data_type.upper() == expected_type and metadata.unit == expected_unit:
            print("\n✅ SUCCESS: Metadata verified!")
            print(f"Requirement FR6 (Verify Signal Type) implemented.")
        else:
            print("\n❌ FAIL: Metadata check failed.")
            print(f"Expected Type: '{expected_type}', Found: '{metadata.data_type}'")

except Exception as e:
    print(f"\nERROR: {e}")