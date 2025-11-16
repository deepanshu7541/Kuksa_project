"""
Example usage of SUMO distance-based auto-braking integration.

This script demonstrates how to use the SUMO integration module
to monitor vehicle distance and trigger automatic braking.
"""

from speedMonitor.sumo_integration import SUMODistanceMonitor


def main():
    """Example: Run SUMO simulation with distance monitoring."""
    
    # Configuration
    sumo_config = "sumo/highway.sumocfg"
    distance_threshold = 50.0  # meters - trigger brake when distance < 50m
    kuksa_ip = "127.0.0.1"
    kuksa_port = 55556
    
    print("=" * 60)
    print("SUMO Distance-Based Auto-Braking Example")
    print("=" * 60)
    print(f"Config: {sumo_config}")
    print(f"Distance Threshold: {distance_threshold} meters")
    print(f"KUKSA Databroker: {kuksa_ip}:{kuksa_port}")
    print("=" * 60)
    print()
    
    # Create monitor
    monitor = SUMODistanceMonitor(
        sumo_config_path=sumo_config,
        leading_vehicle_id="car_leading",
        following_vehicle_id="car_following",
        distance_threshold=distance_threshold,
        kuksa_ip=kuksa_ip,
        kuksa_port=kuksa_port,
        update_interval=0.1  # Check every 0.1 seconds
    )
    
    try:
        # Start simulation (set gui=True to see visualization)
        monitor.start_simulation(gui=False)
        
        # Begin monitoring - this will run until simulation ends or Ctrl+C
        monitor.monitor()
        
    except KeyboardInterrupt:
        print("\n[Example] Simulation interrupted by user")
    except Exception as e:
        print(f"\n[Example] Error: {e}")
    finally:
        monitor.close()
        print("[Example] Example completed")


if __name__ == "__main__":
    main()

