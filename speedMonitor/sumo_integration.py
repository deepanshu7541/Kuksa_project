"""
SUMO Integration Module for Distance-Based Auto-Braking System

This module integrates SUMO traffic simulation with the KUKSA AutoBrakeSystem.
It monitors the distance between two vehicles on a straight highway and triggers
automatic braking when the distance falls below a threshold.
"""

import os
import sys
import time
import traci
from typing import Optional, Tuple
from speedMonitor.brake_controller import AutoBrakeSystem


class SUMODistanceMonitor:
    """
    Monitors distance between two vehicles in SUMO simulation and triggers
    AutoBrakeSystem when distance falls below threshold.
    """
    
    def __init__(
        self,
        sumo_config_path: str,
        leading_vehicle_id: str = "car_leading",
        following_vehicle_id: str = "car_following",
        distance_threshold: float = 50.0,  # meters
        kuksa_ip: str = "127.0.0.1",
        kuksa_port: int = 55556,
        update_interval: float = 0.1,  # seconds
        duration: float = 60.0  # seconds - simulation duration
    ):
        """
        Initialize SUMO Distance Monitor.
        
        Args:
            sumo_config_path: Path to SUMO configuration file (.sumocfg)
            leading_vehicle_id: ID of the leading vehicle in SUMO
            following_vehicle_id: ID of the following vehicle (monitored vehicle)
            distance_threshold: Minimum safe distance in meters
            kuksa_ip: KUKSA Databroker IP address
            kuksa_port: KUKSA Databroker port
            update_interval: Time between distance checks (seconds)
            duration: Maximum simulation duration in seconds (0 = unlimited)
        """
        self.sumo_config_path = sumo_config_path
        self.leading_vehicle_id = leading_vehicle_id
        self.following_vehicle_id = following_vehicle_id
        self.distance_threshold = distance_threshold
        self.update_interval = update_interval
        self.duration = duration
        
        self.brake_system = AutoBrakeSystem(
            ip=kuksa_ip,
            port=kuksa_port,
            threshold=0,  # Will be set based on current speed
            reduction_rate=5  # Moderate braking
        )
        
        self.brake_active = False
        self.sumo_running = False
        
    def start_simulation(self, gui: bool = False):
        """
        Start SUMO simulation and begin monitoring.
        
        Args:
            gui: If True, launch SUMO GUI. If False, run headless.
        """
        sumo_binary = "sumo-gui" if gui else "sumo"
        sumo_cmd = [
            sumo_binary,
            "-c", self.sumo_config_path,
            "--step-length", str(self.update_interval),
            "--no-warnings", "false"
        ]
        
        try:
            traci.start(sumo_cmd)
            self.sumo_running = True
            print(f"[SUMO] Simulation started (GUI: {gui})")
            print(f"[SUMO] Monitoring distance between '{self.leading_vehicle_id}' and '{self.following_vehicle_id}'")
            print(f"[SUMO] Distance threshold: {self.distance_threshold} meters")
        except Exception as e:
            print(f"[SUMO] Error starting simulation: {e}")
            raise
    
    def get_distance(self) -> Optional[float]:
        """
        Calculate the distance between leading and following vehicles.
        
        Returns:
            Distance in meters, or None if vehicles not found
        """
        try:
            if not traci.simulation.getMinExpectedNumber() > 0:
                return None
            
            # Check if both vehicles exist
            vehicle_ids = traci.vehicle.getIDList()
            if self.leading_vehicle_id not in vehicle_ids or self.following_vehicle_id not in vehicle_ids:
                return None
            
            # Get positions
            leading_pos = traci.vehicle.getPosition(self.leading_vehicle_id)
            following_pos = traci.vehicle.getPosition(self.following_vehicle_id)
            
            # Calculate Euclidean distance
            distance = ((leading_pos[0] - following_pos[0])**2 + (leading_pos[1] - following_pos[1])**2)**0.5
            
            return distance
        except Exception as e:
            print(f"[SUMO] Error calculating distance: {e}")
            return None
    
    def get_following_vehicle_speed(self) -> Optional[float]:
        """
        Get the speed of the following vehicle.
        
        Returns:
            Speed in m/s, or None if vehicle not found
        """
        try:
            vehicle_ids = traci.vehicle.getIDList()
            if self.following_vehicle_id not in vehicle_ids:
                return None
            
            speed_ms = traci.vehicle.getSpeed(self.following_vehicle_id)
            return speed_ms
        except Exception as e:
            print(f"[SUMO] Error getting vehicle speed: {e}")
            return None
    
    def apply_brake_in_sumo(self, decel: float = 2.0):
        """
        Apply braking to the following vehicle in SUMO.
        
        Args:
            decel: Deceleration rate in m/s²
        """
        try:
            vehicle_ids = traci.vehicle.getIDList()
            if self.following_vehicle_id not in vehicle_ids:
                return
            
            current_speed = traci.vehicle.getSpeed(self.following_vehicle_id)
            new_speed = max(0, current_speed - decel * self.update_interval)
            traci.vehicle.setSpeed(self.following_vehicle_id, new_speed)
        except Exception as e:
            print(f"[SUMO] Error applying brake: {e}")
    
    def monitor(self):
        """
        Main monitoring loop. Checks distance and triggers braking when needed.
        """
        if not self.sumo_running:
            print("[SUMO] Simulation not running. Call start_simulation() first.")
            return
        
        step = 0
        vehicle_tracked = False
        start_time = None
        
        if self.duration > 0:
            print(f"[SUMO] Starting distance monitoring loop (duration: {self.duration} seconds)...")
        else:
            print("[SUMO] Starting distance monitoring loop (unlimited duration)...")
        
        try:
            while traci.simulation.getMinExpectedNumber() > 0:
                traci.simulationStep()
                step += 1
                
                # Get current simulation time
                current_time = traci.simulation.getTime()
                if start_time is None:
                    start_time = current_time
                
                # Check if duration limit reached
                if self.duration > 0 and (current_time - start_time) >= self.duration:
                    print(f"[SUMO] Simulation duration limit reached ({self.duration} seconds). Stopping...")
                    break
                
                # Track vehicle in GUI view once it's loaded (only once)
                if not vehicle_tracked:
                    try:
                        vehicle_ids = traci.vehicle.getIDList()
                        if self.following_vehicle_id in vehicle_ids:
                            # Set initial view settings
                            traci.gui.setBoundary("View #0", 0, -50, 2000, 50)
                            traci.gui.setZoom("View #0", 500)  # Zoom in closer
                            # Track the following vehicle
                            traci.gui.trackVehicle("View #0", self.following_vehicle_id)
                            
                            # Enable raster images for better vehicle visualization
                            # This makes custom car images visible if imgFile is set in route file
                            try:
                                traci.gui.setSchema("View #0", "vehicle")
                                # Try to set vehicle shape to raster if custom images are used
                                # Note: This may need to be set manually in GUI: View Settings > Vehicle Shape > raster images
                            except:
                                pass
                            
                            vehicle_tracked = True
                            print("[SUMO] Vehicle tracking enabled in GUI")
                            print("[SUMO] Tip: In SUMO GUI, go to View Settings > Vehicle Shape > select 'raster images' for custom car images")
                    except Exception as e:
                        # GUI might not be available or not ready yet
                        if step < 10:  # Only print error in first few steps
                            pass
                
                distance = self.get_distance()
                speed_ms = self.get_following_vehicle_speed()
                
                if distance is not None and speed_ms is not None:
                    speed_kmh = speed_ms * 3.6  # Convert m/s to km/h
                    
                    if step % 10 == 0:  # Print every 10 steps
                        print(f"[SUMO] Step {step}: Distance = {distance:.2f}m, Speed = {speed_kmh:.2f} km/h")
                    
                    # Check if distance is below threshold
                    if distance < self.distance_threshold:
                        if not self.brake_active:
                            print(f"\n[SUMO] ⚠️ WARNING: Distance {distance:.2f}m below threshold {self.distance_threshold}m!")
                            print(f"[SUMO] Activating AutoBrakeSystem for following vehicle...")
                            self.brake_active = True
                            
                            # Trigger KUKSA AutoBrakeSystem
                            # The brake system expects speed in km/h
                            self.brake_system.engage_brake(speed_kmh)
                        
                        # Also apply brake directly in SUMO
                        self.apply_brake_in_sumo(decel=4.5)
                    else:
                        # Distance is safe, reset brake state
                        if self.brake_active:
                            print(f"[SUMO] Distance {distance:.2f}m is now safe. Releasing brake.")
                            self.brake_active = False
                            self.brake_system.active = False
                
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            print("\n[SUMO] Monitoring stopped by user.")
        except Exception as e:
            print(f"[SUMO] Error in monitoring loop: {e}")
        finally:
            self.close()
    
    def close(self):
        """Close SUMO simulation."""
        if self.sumo_running:
            traci.close()
            self.sumo_running = False
            print("[SUMO] Simulation closed.")


def run_sumo_simulation(
    sumo_config_path: str,
    distance_threshold: float = 50.0,
    gui: bool = False,
    kuksa_ip: str = "127.0.0.1",
    kuksa_port: int = 55556,
    duration: float = 60.0
):
    """
    Convenience function to run SUMO simulation with distance monitoring.
    
    Args:
        sumo_config_path: Path to SUMO configuration file
        distance_threshold: Minimum safe distance in meters
        gui: Whether to show SUMO GUI
        kuksa_ip: KUKSA Databroker IP
        kuksa_port: KUKSA Databroker port
        duration: Maximum simulation duration in seconds (0 = unlimited)
    """
    monitor = SUMODistanceMonitor(
        sumo_config_path=sumo_config_path,
        distance_threshold=distance_threshold,
        kuksa_ip=kuksa_ip,
        kuksa_port=kuksa_port,
        duration=duration
    )
    
    try:
        monitor.start_simulation(gui=gui)
        monitor.monitor()
    except Exception as e:
        print(f"[SUMO] Fatal error: {e}")
        monitor.close()
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SUMO Distance-Based Auto-Braking Simulation")
    parser.add_argument("--config", default="sumo/highway.sumocfg", help="Path to SUMO config file")
    parser.add_argument("--threshold", type=float, default=50.0, help="Distance threshold in meters")
    parser.add_argument("--gui", action="store_true", help="Launch SUMO GUI")
    parser.add_argument("--kuksa-ip", default="127.0.0.1", help="KUKSA Databroker IP")
    parser.add_argument("--kuksa-port", type=int, default=55556, help="KUKSA Databroker port")
    parser.add_argument("--duration", type=float, default=60.0, help="Simulation duration in seconds (0 = unlimited)")
    
    args = parser.parse_args()
    
    run_sumo_simulation(
        sumo_config_path=args.config,
        distance_threshold=args.threshold,
        gui=args.gui,
        kuksa_ip=args.kuksa_ip,
        kuksa_port=args.kuksa_port,
        duration=args.duration
    )

