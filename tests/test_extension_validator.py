import pytest
from time import sleep
from kuksa_client.grpc import VSSClient

DATABROKER_ADDR = '127.0.0.1'
DATABROKER_PORT = 55556
SPEED_SIGNAL = 'Vehicle.Speed'
MAX_SPEED = 300.0 # Realistic Quality Gate Limit (FX1)

@pytest.mark.extension # Group this as the extension test suite (NX1)
def test_speed_quality_gate_validation():
    """
    FX1: Implements the Automated Trace Validator to check data quality and dynamics.
    """
    print(f"\n--- Starting Automated Trace Validator Test for {SPEED_SIGNAL} ---")
    
    client = VSSClient(DATABROKER_ADDR, DATABROKER_PORT)
    try:
        client.connect()
    except Exception as e:
        pytest.fail(f"Could not connect to Databroker: {e}. Check Docker Compose.")

    # Read values v1 and v2 (simulating a trace stream check)
    v1 = client.get_current_values([SPEED_SIGNAL])[SPEED_SIGNAL].value
    sleep(1.0)
    v2 = client.get_current_values([SPEED_SIGNAL])[SPEED_SIGNAL].value

    # 1. Check for non-negative values
    assert v1 >= 0 and v2 >= 0, f"Quality Gate FAIL: Value is negative. V1: {v1}, V2: {v2}"

    # 2. Check for realistic maximum speed (Custom Quality Gate - FX1)
    assert v1 <= MAX_SPEED and v2 <= MAX_SPEED, \
        f"Quality Gate FAIL: Value {v2} exceeds max realistic speed {MAX_SPEED} km/h."

    # 3. Check for dynamic change (F7/Trace Replay validation)
    assert v1 != v2, "Quality Gate FAIL: Signal is static, Mock Provider replay may be broken (F7)."

    print("--- Automated Trace Validator PASSED all quality gates (FX1, F7) ---")