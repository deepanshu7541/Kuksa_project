# SUMO Integration for Distance-Based Auto-Braking

This directory contains SUMO (Simulation of Urban MObility) configuration files and integration code for simulating a straight highway scenario with distance-based automatic braking.

## Overview

The SUMO integration monitors the distance between two vehicles on a straight highway. When the distance falls below a configurable threshold, the system triggers the AutoBrakeSystem to slow down the following vehicle.

## Files

- `highway.net.xml` - SUMO network definition for a straight 2km highway with 2 lanes
- `highway.rou.xml` - Route definition with two vehicles (leading and following)
- `highway.sumocfg` - SUMO simulation configuration file

## Prerequisites

### 1. Install SUMO

SUMO must be installed separately from Python packages. Choose one of the following methods:

#### Windows:
```bash
# Using Chocolatey
choco install sumo

# Or download from: https://sumo.dlr.de/docs/Downloads.php
```

#### Linux:
```bash
sudo add-apt-repository ppa:sumo/stable
sudo apt-get update
sudo apt-get install sumo sumo-tools
```

#### macOS:
```bash
brew install sumo
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install `sumolib` which provides the TraCI Python interface.

### 3. Verify SUMO Installation

```bash
sumo --version
```

You should see the SUMO version number.

## Usage

### Basic Usage (Headless)

```bash
python -m speedMonitor.sumo_integration --config sumo/highway.sumocfg --threshold 50.0
```

### With GUI (Visual)

```bash
python -m speedMonitor.sumo_integration --config sumo/highway.sumocfg --threshold 50.0 --gui
```

### Command Line Arguments

- `--config`: Path to SUMO configuration file (default: `sumo/highway.sumocfg`)
- `--threshold`: Distance threshold in meters (default: 50.0)
- `--gui`: Launch SUMO GUI for visualization
- `--kuksa-ip`: KUKSA Databroker IP address (default: 127.0.0.1)
- `--kuksa-port`: KUKSA Databroker port (default: 55556)

### Programmatic Usage

```python
from speedMonitor.sumo_integration import SUMODistanceMonitor

# Create monitor
monitor = SUMODistanceMonitor(
    sumo_config_path="sumo/highway.sumocfg",
    distance_threshold=50.0,  # meters
    kuksa_ip="127.0.0.1",
    kuksa_port=55556
)

# Start simulation (headless)
monitor.start_simulation(gui=False)

# Begin monitoring
monitor.monitor()
```

## How It Works

1. **Simulation Setup**: SUMO creates a straight highway with two vehicles
   - `car_leading`: Front vehicle (starts at position 100m, speed 25 m/s)
   - `car_following`: Rear vehicle (starts at position 50m, speed 30 m/s)

2. **Distance Monitoring**: The system continuously calculates the Euclidean distance between the two vehicles

3. **Brake Trigger**: When distance < threshold:
   - Activates AutoBrakeSystem via KUKSA Databroker
   - Applies braking directly in SUMO simulation
   - Logs warnings and status updates

4. **Brake Release**: When distance >= threshold:
   - Releases brake
   - Resets brake system state

## Integration with KUKSA

The SUMO integration connects to the KUKSA Databroker and uses the existing `AutoBrakeSystem` class to control vehicle speed. When a dangerous distance is detected:

1. SUMO calculates the distance between vehicles
2. If below threshold, `AutoBrakeSystem.engage_brake()` is called
3. The brake system reduces speed via KUKSA `Vehicle.Speed` signal
4. SUMO also applies braking directly in the simulation for visual feedback

## Customization

### Adjust Distance Threshold

Modify the threshold when creating the monitor:
```python
monitor = SUMODistanceMonitor(distance_threshold=30.0)  # 30 meters
```

### Modify Vehicle Behavior

Edit `highway.rou.xml` to change:
- Initial positions (`departPos`)
- Initial speeds (`departSpeed`)
- Vehicle types and characteristics

### Change Highway Length

Edit `highway.net.xml` to modify the highway length (currently 2000m).

## Troubleshooting

### SUMO Not Found
If you get "sumo: command not found", ensure SUMO is installed and in your PATH:
```bash
export SUMO_HOME=/usr/share/sumo  # Linux
# or
set SUMO_HOME=C:\Program Files\sumo  # Windows
```

### TraCI Connection Errors
- Ensure SUMO is properly installed
- Check that the config file path is correct
- Verify network and route files exist

### KUKSA Connection Errors
- Ensure KUKSA Databroker is running
- Check IP and port settings
- Verify kuksa-client is installed

