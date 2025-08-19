# Health Sensor Simulator

## Project Description
**Health Sensor Simulator** is a comprehensive health monitoring simulation platform built with **FastAPI** and **Streamlit**. It simulates realistic wearable health device data including heart rate, breathing rate, blood oxygen saturation, blood pressure, and body temperature. The system features an interactive web interface for real-time data visualization and parameter configuration.

![User Interface](./docs/diagrams/streamlit_ui_anomaly.png)

## Key Features
- **FastAPI-based REST API** with OpenAPI documentation
- **Dual Anomaly Detection** using Extended Isolation Forest (EIF) or distance-based methods
- **Intelligent Alarm System** with HTTP POST notifications to external endpoints when anomalies are detected
- **Trained EIF Model** (`eif.joblib`) for machine learning-based anomaly detection  
- **Real-time Data Simulation** to generate realistic vital sign measurements
- **Interactive Streamlit UI** for configuring health parameters and visualization
- **Environment-based Configuration** with `.env` file support and variable precedence
- **Comprehensive Test Suite** with 148 unit tests covering all functionality
- **Inter-process Communication** for synchronized data between UI and API
- **Dockerized Deployment** for consistent containerized environments

![System Architecture](./docs/diagrams/system_architecture.png)

The Health Sensor Simulator is part of a stack of applications that allow a user to track the metrics and get notified of alarms in real time, and analyze historical values, using intuitive dashboards. The stack's project is located in this [link](https://github.com/marcoom/health-anomaly-detector-stack).

![Health Anomaly Detector Stack](./docs/diagrams/compose_app.png)

## Current Functionality
### Working Features
- **FastAPI REST API** with OpenAPI documentation
- **Streamlit Web Interface** with interactive health parameter controls
- **Real-time Data Generation** with configurable variance and automatic refresh
- **Health Data Visualization** using radial distance plots
- **Parameter Validation** with realistic health value ranges
- **Integrated Launcher** running both services from single command

### API Endpoints
- `GET /api/v1/version` - Returns the service version
- `GET /api/v1/vitals` - Returns the latest readings of all health variables

### Anomaly Detection & Alarms
- **Dual Detection Methods**: Extended Isolation Forest (EIF) or distance-based statistical analysis
- **Automatic Alarms**: HTTP POST notifications sent to configurable endpoints when anomalies are detected
- **Configurable Thresholds**: Separate thresholds for EIF (probability-based) and distance methods
- **Real-time Processing**: Anomaly detection runs continuously on generated health data

## Environment Configuration

The application supports flexible configuration through environment variables and `.env` file. Configuration follows this precedence: **Environment Variables** > **`.env` file** > **Default values**.

### Configuration Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`) |
| `ANOMALY_DETECTION_METHOD` | `DISTANCE` | Detection method (`DISTANCE`, `EIF`) |
| `EIF_THRESHOLD` | `0.4` | EIF anomaly threshold (0.0-1.0) |
| `DISTANCE_THRESHOLD` | `3.8` | Distance method threshold |
| `ALARM_ENDPOINT_URL` | `None` | HTTP endpoint for anomaly notifications |
| `FASTAPI_HOST` | `0.0.0.0` | FastAPI server host |
| `FASTAPI_PORT` | `8000` | FastAPI server port |
| `STREAMLIT_HOST` | `0.0.0.0` | Streamlit server host |
| `STREAMLIT_PORT` | `8501` | Streamlit server port |

### Example .env File
```bash
# Health Sensor Simulator Environment Configuration

# Alarm system configuration
ALARM_ENDPOINT_URL=http://localhost:8080/alerts

# Anomaly detection configuration  
ANOMALY_DETECTION_METHOD=EIF
EIF_THRESHOLD=0.4
DISTANCE_THRESHOLD=3.8

# Logging configuration
LOG_LEVEL=INFO
```

---

## Requirements
- **Python**: 3.11  
- **pip** and **virtualenv** (recommended)  
- For Docker usage: Docker Engine 20.10+  

---

## Installation & Running

### 1. Clone the repository
```bash
git clone https://github.com/marcoom/health-sensor-simulator.git
cd health-sensor-simulator
```

### 2. Environment Setup
```bash
# Create virtual environment (Python 3.11 required)
python3.11 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# Install dependencies using Makefile
make install-dev            # Installs all dependencies including dev tools
# OR install only production dependencies
make install               # Production dependencies only
```

### 3. Run the Service
```bash
# Method 1: Integrated mode - FastAPI + Streamlit (recommended)
python -m src.main

# Method 2: Using the Makefile (same as Method 1)
make run

# Method 3: FastAPI only
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the Service
- **Streamlit UI**: [http://localhost:8501](http://localhost:8501) - Interactive health parameter controls and visualization
- **API Base URL**: [http://localhost:8000](http://localhost:8000)
- **Interactive API Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)  
- **Alternative API Documentation (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 5. Test the API
```bash
# Test the version endpoint
curl http://localhost:8000/api/v1/version
# Expected response: {"version":"0.1.0"}

# Test the vitals endpoint
curl http://localhost:8000/api/v1/vitals
# Expected response: {"ts":"2024-01-01T12:00:00Z","heart_rate":80,"oxygen_saturation":98,...}
```  

---

### Running with Docker
Build and run the container:
```bash
# Using Makefile commands (recommended)
make docker-build
make docker-run

# OR using Docker directly
docker build -t health-sensor-simulator .
docker run -p 8000:8000 health-sensor-simulator
```

---

## Development & Testing

### Documentation
The full user and API guide is deployed to GitHub Pages, and can be found at this [link](https://marcoom.github.io/health-sensor-simulator/).

### Running Tests
```bash
# Run all tests
make test

# Run tests with coverage report
make test-coverage

# Run tests manually with pytest
pytest tests/ -v
```

### Development Setup
```bash
# Install development dependencies
make install-dev

# This includes:
# - pytest for testing
# - coverage for test coverage
# - httpx for async HTTP testing
# - All documentation tools
```

### Building Documentation
```bash
# Build HTML documentation
make docs-html

# Build PDF documentation (requires LaTeX)
make docs-pdf

# Clean documentation build files
make docs-clean
```

---

## Project Structure
```text
.
├── .env                          # Environment configuration file
├── data/                         # Datasets and processed data
│   └── processed/                # Processed health variables dataset
├── docs/                         # Project documentation (Sphinx, diagrams)
├── src/                          # Main application package
│   ├── app/
│   │   ├── api/                  # FastAPI routes and schemas
│   │   │   ├── routes.py         # API endpoints (/version, /vitals)
│   │   │   └── schemas.py        # Pydantic models (VitalsResponse, AnomalyResponse)
│   │   ├── constants/            # Health parameters and constants
│   │   │   └── health_params.py  # Health variable specifications
│   │   ├── services/             # Business logic layer
│   │   │   ├── data_simulator.py # Health data generation and IPC
│   │   │   ├── anomaly_detector.py # EIF & distance anomaly detection
│   │   │   └── alarm_client.py   # HTTP alarm notifications
│   │   ├── ui/                   # Streamlit UI components
│   │   │   ├── streamlit_app.py  # Main Streamlit application
│   │   │   ├── config.py         # UI configuration and sliders
│   │   │   ├── helpers.py        # UI helper functions
│   │   │   └── visualization.py  # Health data visualization
│   │   ├── utils/                # Utility functions
│   │   │   ├── logging.py        # Logging configuration
│   │   │   └── math_utils.py     # Mathematical utilities
│   │   ├── config.py             # Application configuration management
│   │   └── version.py            # Version information
│   ├── models/                   # Trained ML models
│   │   └── eif.joblib           # Extended Isolation Forest model
│   └── main.py                   # Integrated application launcher
├── notebooks/                    # Jupyter notebooks for data generation and model training
├── tests/                        # Comprehensive test suite (148 tests)
│   ├── test_api.py              # API endpoint tests (21 tests)
│   ├── test_config_environment.py # Environment configuration tests (18 tests)
│   ├── test_logging.py          # Logging configuration tests
│   ├── test_constants/          # Constants and parameters tests
│   ├── test_services/           # Business logic tests including alarm notifications
│   │   ├── test_anomaly_detector.py # Anomaly detection tests (24 tests)
│   │   ├── test_alarm_notifications.py # Alarm system tests (7 tests)
│   │   └── test_data_simulator.py # Data simulation tests
│   ├── test_ui/                 # UI component tests
│   └── test_utils/              # Utility function tests
└── requirements/                 # Dependencies (base, dev, docs)
```

---

## License
This project is licensed under the **MIT License** — you are free to use, modify, and distribute it, with attribution. See the [LICENSE](LICENSE) file for details.
