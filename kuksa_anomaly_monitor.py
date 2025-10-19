import sys
import os
# Fix ModuleNotFound by ensuring the current directory is in the path
sys.path.append(os.path.dirname(__file__))

import argparse, time, signal
from kuksa_client.grpc import VSSClient, VSSClientError
from speedMonitor.core import SpeedMonitor, Thresholds
from speedMonitor.io import AlertSink

# --- 1. Argument Parsing ---
def parse_args():
    p = argparse.ArgumentParser(description="Speed Anomaly Monitor (Phase 1 scaffold)")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=55556)
    p.add_argument("--max-speed", type=float, default=80.0)
    p.add_argument("--csv", default="alerts.csv")
    p.add_argument("--hz", type=float, default=1.0, help="Polling frequency in Hz")
    return p.parse_args()

# --- 2. Main Execution (POLLING METHOD) ---
def main():
    args = parse_args()
    mon  = SpeedMonitor(Thresholds(args.max_speed))
    sink = AlertSink(args.csv)

    c = VSSClient(args.host, args.port)
    
    try:
        # Establish Connection
        c.connect()
        print(f"✅ Broker Connection Confirmed.")

        # Polling frequency calculation
        period = 1.0 / max(1e-6, args.hz)
        print(f"Polling Vehicle.Speed at {1.0/period:.1f} Hz. Monitoring speed (Max: {args.max_speed} km/h). Ctrl+C to exit.")

        running = True
        def _stop(*_):
            nonlocal running; running = False
        signal.signal(signal.SIGINT, _stop)
        signal.signal(signal.SIGTERM, _stop)
        
        while running:
            # 1. SYNCHRONOUSLY GET DATA
            cur = c.get_current_values(["Vehicle.Speed"])
            speed = cur["Vehicle.Speed"].value

            # 2. RUN MONITOR LOGIC
            alerts = mon.on_speed(speed)
            
            # 3. LOG ALERTS using the required sink.write() method
            for a in alerts:
                # Use the Alert object's properties to call the sink.write function
                sink.write(a.kind, a.speed, a.reason)

            # 4. PAUSE
            time.sleep(period)
            
    except KeyboardInterrupt:
        print("\nInterrupted, exiting…")
    except VSSClientError as e:
        print(f"\nConnection Error: {e.reason}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        sink.close()
        try:
            c.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()

# import sys
# import os
# # Fix ModuleNotFound by ensuring the current directory is in the path
# sys.path.append(os.path.dirname(__file__))

# # Standard Libraries
# import argparse, time, signal
# from kuksa_client.grpc import VSSClient, VSSClientError
# from speedMonitor.core import SpeedMonitor, Thresholds
# from speedMonitor.io import AlertSink

# # --- 1. Argument Parsing ---
# def parse_args():
#     p = argparse.ArgumentParser(description="Speed Anomaly Monitor (Phase 1 scaffold)")
#     p.add_argument("--host", default="127.0.0.1")
#     p.add_argument("--port", type=int, default=55556)
#     p.add_argument("--max-speed", type=float, default=80.0)
#     p.add_argument("--csv", default="alerts.csv")
#     return p.parse_args()

# # --- 2. Main Execution ---
# def main():
#     args = parse_args()
#     # Note: args.max_speed is currently 10.0 from the command line
#     mon = SpeedMonitor(Thresholds(args.max_speed))
#     sink = AlertSink(args.csv)
    
#     # Setup for clean shutdown
#     running = True
#     def _stop(*_):
#         nonlocal running
#         print("\nStopping subscription...")
#         running = False
        
#     signal.signal(signal.SIGINT, _stop)
#     signal.signal(signal.SIGTERM, _stop)
    
#     try:
#         # Connect to Data Broker (FR2)
#         with VSSClient(args.host, args.port) as c:
            
#             # --- CONNECTION STATUS CHECK (Simplified) ---
#             # Your successful connection is sufficient proof the broker is up.
#             print("✅ Broker Connection Confirmed.")
#             print(f"Connected to {args.host}:{args.port}. Monitoring speed (Max: {args.max_speed} km/h)...")

#             # --- Subscription Handler (FR8) ---
#             def on_update(resp):
#                 # FR7: Get dynamic speed value
#                 if "Vehicle.Speed" in resp:
#                     speed = resp["Vehicle.Speed"].value
                    
#                     # Core Logic: Check for anomalies
#                     alerts = mon.on_speed(speed)

#                     print(f"Monitor ran. Alerts generated: {len(alerts)}") 
                    
#                     # Log any anomalies detected
#                     if alerts:
#                         sink.log(alerts)
            
#             # Start continuous subscription stream using correct keyword arguments
#             c.subscribe_current_values(paths=["Vehicle.Speed"], callback=on_update)
#             print("Subscribed. Press Ctrl+C to exit.")

#             # Keep the main thread alive to receive updates
#             while running:
#                 time.sleep(0.2)

#     except VSSClientError as e:
#         print(f"Connection Error: {e.reason}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
        
#     finally:
#         sink.close()

# if __name__ == "__main__":
#     main()