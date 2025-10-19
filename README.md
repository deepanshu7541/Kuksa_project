# Kuksa Testing Lab

A testing environment for Eclipse Kuksa Databroker with mock vehicle data providers. This project enables local development and integration testing of vehicle signal specifications (VSS) using containerized services.

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- pip (Python package installer)

## For Windows

Add this code under COPY ./ in Dockerfile (third_party/kuksa-mock-provider/Dockerfile) 

RUN apt-get update && apt-get install -y dos2unix \
    && find . -type f \( -name "*.py" -o -name "*.sh" \) -exec dos2unix {} \;

    

## Getting Started

### 1. Start Databroker and Mock Provider

From the project root folder, start the containerized services:

```bash
docker compose up -d
```

Verify the services are running:

```bash
docker compose logs
```

### 2. Prepare Python Virtual Environment

Activate the virtual environment:

```bash
source .venv/bin/activate
```

> **Note:** Ensure you've created the virtual environment and installed dependencies first:
> ```bash
> python3 -m venv .venv
> source .venv/bin/activate
> pip install -r requirements.txt
> ```

### 3. Run Integration Tests

Execute the integration test suite:

```bash
pytest -m integration -q
```

The tests will:
- Connect to the Databroker at port 55556
- Verify that `Vehicle.Speed` is available
- Validate that speed values are non-negative

### 4. Manually Read Speed Values

To manually query speed values and verify they're updating:

```bash
python3 - <<'PY'
from time import sleep
from kuksa_client.grpc import VSSClient

c = VSSClient('127.0.0.1', 55556)
c.connect()

v1 = c.get_current_values(['Vehicle.Speed'])['Vehicle.Speed'].value
sleep(1.0)
v2 = c.get_current_values(['Vehicle.Speed'])['Vehicle.Speed'].value

print("Vehicle.Speed v1:", v1)
print("Vehicle.Speed v2:", v2, " (should be different)")
PY
```

### 5. Subscribe to Speed Updates

Run the demo script to subscribe to real-time speed updates:

```bash
python demo_subscribe_speed.py
```

## Project Structure

```
.
├── docker-compose.yml
├── .venv/
├── demo_subscribe_speed.py
├── tests/
│   └── integration/
└── README.md
```

## Configuration

- **Databroker Port:** 55556 (gRPC)
- **VSS Signal:** `Vehicle.Speed`

## Troubleshooting

**Services won't start:**
- Check Docker daemon is running
- Verify ports 55556 is available
- Review logs with `docker compose logs`

**Connection refused:**
- Ensure containers are running: `docker compose ps`
- Verify firewall settings aren't blocking port 55556

**Import errors:**
- Confirm virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Contributors

- Chao Meng
- Deepanshu Chand
- Quang Thong Phung
- Harsh Vardhan
- Anuj Kumar
