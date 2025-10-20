# KUKSA Anomaly Detection and Speed Alert System

## Introduction
This project extends the **Eclipse KUKSA** automotive data framework by adding an **Anomaly Detection and Speed Alert System**.  
It monitors real-time vehicle speed data from the KUKSA Databroker, detects abnormal variations, and logs alerts into a CSV file for analysis.  
The project demonstrates the use of Python-based microservices integrated with the KUKSA ecosystem for automotive software testing and safety monitoring.

---

## How to Set Up and Run the Project

### 1️Clone the Repository
```bash
git clone https://github.com/deepanshu7541/Kuksa_project.git
cd Kuksa_project
```
### 🔑 Core Features Implemented:

1.  **Speed Anomaly Monitor:** Logs a **`SPEEDING`** alert if `Vehicle.Speed` exceeds a user-defined threshold (`--max-speed`).
2.  **Implausibility Detection:** Logs a **`CRITICAL_CONFLICT`** alert if **Brake** and **Accelerator** positions exceed a low, defined threshold (`--max-brake-accel`) simultaneously.
3.  **Reliable Polling:** The client uses the **synchronous `get_current_values()`** method to ensure data is reliably fetched and processed at a fixed frequency (`--hz`).
4.  **Data Logging:** All detected anomalies are logged to `alerts.csv` and printed to the console.

---

## 🛠️ How to Set Up and Run the Project
```bash
### 1️⃣ Prerequisites and Setup
Ensure you have **Docker** and **Docker Compose** installed. You will also need **Python 3.8+** and the necessary dependencies (e.g., `kuksa-client`).

### 2️⃣ Start KUKSA Services
Navigate to your main KUKSA directory (where your `docker-compose.yml` is located) and start the Data Broker and Mock Provider in the background:
```

---

## Phase one Overview

The phase one focuses on the Speed ​​Anomaly Monitor system, it also includes several **test and validation scripts** to ensure full system functionality with the Eclipse KUKSA Databroker:

| Script | Purpose | Key Features |
|--------|----------|---------------|
| **kuksa_client_test.py** | Validates the KUKSA client connection and data retrieval. | Connects to the Databroker, fetches `Vehicle.Speed`, and subscribes for 5 live updates. |
| **kuksa_metadata_test.py** | Verifies metadata accuracy for vehicle signals. | Checks that `Vehicle.Speed` has correct data type (`FLOAT`) and unit (`km/h`). |
| **kuksa_read_speed.py** | Tests signal dynamics. | Reads speed twice and confirms if the signal value changes over time. |
| **kuksa_subscribe_test.py** | Demonstrates continuous subscription capability. | Subscribes to `Vehicle.Speed` for 10 updates to confirm stable streaming. |
| **kuksa_actuator_test.py** | Demonstrates actuator control functionality. | Sends and confirms write commands to control `Vehicle.Body.Windshield.Front.Wiping.System.TargetPosition`. |
| **kuksa_anomaly_monitor.py** | Main anomaly detection module. | Periodically polls vehicle speed, detects overspeed events, and logs alerts to `alerts.csv`. |

### Core Package: `speedMonitor/`
Contains the reusable modules that power the system logic:
- `core.py`: Implements the `SpeedMonitor` and `Thresholds` classes for anomaly detection.
- `io.py`: Implements the `AlertSink` class for CSV logging.
- `main.py`: Provides the main execution interface.

### Tests Directory: `tests/`
Includes pytest-based scripts for integration and extension validation.

---