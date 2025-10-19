# KUKSA Anomaly Detection and Speed Alert System

## Introduction
This project extends the **Eclipse KUKSA** automotive data framework by adding an **Anomaly Detection and Speed Alert System**.  
It monitors real-time vehicle speed data from the KUKSA Databroker, detects abnormal variations, and logs alerts into a CSV file for analysis.  
The project demonstrates the use of Python-based microservices integrated with the KUKSA ecosystem for automotive software testing and safety monitoring.

---

## How to Set Up and Run the Project

### 1️Clone the Repository
```bash
git clone https://github.com/<your-group-repo>/KUKSA-Anomaly-Detection.git
cd KUKSA-Anomaly-Detection
### 🔑 Core Features Implemented:

1.  **Speed Anomaly Monitor:** Logs a **`SPEEDING`** alert if `Vehicle.Speed` exceeds a user-defined threshold (`--max-speed`).
2.  **Implausibility Detection:** Logs a **`CRITICAL_CONFLICT`** alert if **Brake** and **Accelerator** positions exceed a low, defined threshold (`--max-brake-accel`) simultaneously.
3.  **Reliable Polling:** The client uses the **synchronous `get_current_values()`** method to ensure data is reliably fetched and processed at a fixed frequency (`--hz`).
4.  **Data Logging:** All detected anomalies are logged to `alerts.csv` and printed to the console.

---

## 🛠️ How to Set Up and Run the Project

### 1️⃣ Prerequisites and Setup
Ensure you have **Docker** and **Docker Compose** installed. You will also need **Python 3.8+** and the necessary dependencies (e.g., `kuksa-client`).

### 2️⃣ Start KUKSA Services
Navigate to your main KUKSA directory (where your `docker-compose.yml` is located) and start the Data Broker and Mock Provider in the background:
```bash
