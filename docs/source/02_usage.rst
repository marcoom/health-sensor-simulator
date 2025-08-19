Usage
=====

Health Sensor Simulator is a production-ready health monitoring simulation platform with dual anomaly detection methods, intelligent alarm system, and comprehensive configuration options.

Current API Endpoints
---------------------

- ``GET /api/v1/version`` - Returns the service version
- ``GET /api/v1/vitals`` - Returns latest health readings

Local Development
-----------------

Environment Setup
:::::::::::::::::

1. **Clone the repository**::

    $ git clone https://github.com/marcoom/health-sensor-simulator.git
    $ cd health-sensor-simulator

2. **Create virtual environment** (Python 3.11 required)::

    $ python3.11 -m venv .venv
    $ source .venv/bin/activate   # On Windows: .venv\Scripts\activate

3. **Install dependencies**::

    $ make install-dev    # Installs all dependencies including dev tools
    # OR
    $ make install       # Production dependencies only

Running the Integrated Service
::::::::::::::::::::::::::::::

1. **Method 1: Integrated mode - FastAPI + Streamlit (recommended)**::

    $ python -m src.main

2. **Method 2: Using the Makefile (same as Method 1)**::

    $ make run

3. **Method 3: FastAPI only**::

    $ uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

4. **Access the services**:

   - **Streamlit UI**: http://localhost:8501 - Interactive health parameter controls and visualization
   - **API Base URL**: http://localhost:8000
   - **Interactive API Documentation (Swagger UI)**: http://localhost:8000/docs
   - **Alternative API Documentation (ReDoc)**: http://localhost:8000/redoc

5. **Test the API**::

    $ curl http://localhost:8000/api/v1/version
    # Expected response: {"version":"0.1.0"}
    
    $ curl http://localhost:8000/api/v1/vitals
    # Expected response: {"ts":"2024-01-01T12:00:00Z","heart_rate":80,"oxygen_saturation":98,...}

Environment Configuration
:::::::::::::::::::::::::

The application supports flexible configuration through environment variables and ``.env`` file. 
Configuration follows this precedence: **Environment Variables** > **``.env`` file** > **Default values**.

.. list-table:: Environment Variables
   :widths: 15 15 15 40
   :header-rows: 1

   * - Variable
     - Default
     - Type
     - Description
   * - ``LOG_LEVEL``
     - ``INFO``
     - String
     - Logging level (``DEBUG``, ``INFO``, ``WARNING``)
   * - ``ANOMALY_DETECTION_METHOD``
     - ``DISTANCE``
     - String
     - Detection method (``DISTANCE``, ``EIF``)
   * - ``EIF_THRESHOLD``
     - ``0.4``
     - Float
     - EIF anomaly threshold (0.0-1.0)
   * - ``DISTANCE_THRESHOLD``
     - ``3.8``
     - Float
     - Distance method threshold
   * - ``ALARM_ENDPOINT_URL``
     - ``None``
     - String
     - HTTP endpoint for anomaly notifications
   * - ``FASTAPI_HOST``
     - ``0.0.0.0``
     - String
     - FastAPI server host
   * - ``FASTAPI_PORT``
     - ``8000``
     - Integer
     - FastAPI server port
   * - ``STREAMLIT_HOST``
     - ``0.0.0.0``
     - String
     - Streamlit server host
   * - ``STREAMLIT_PORT``
     - ``8501``
     - Integer
     - Streamlit server port

.env File Configuration
+++++++++++++++++++++++

Create a ``.env`` file in the project root directory::

    # Health Sensor Simulator Environment Configuration
    
    # Alarm system configuration
    ALARM_ENDPOINT_URL=http://localhost:8080/alerts
    
    # Anomaly detection configuration
    ANOMALY_DETECTION_METHOD=EIF
    EIF_THRESHOLD=0.4
    DISTANCE_THRESHOLD=3.8
    
    # Logging configuration
    LOG_LEVEL=INFO

Anomaly Detection & Alarms
:::::::::::::::::::::::::::

The system supports two anomaly detection methods:

**Extended Isolation Forest (EIF)**
  - Machine learning-based anomaly detection
  - Uses trained model at ``src/models/eif.joblib``
  - Threshold: probability score (0.0-1.0)
  - More sophisticated detection of complex patterns

**Distance-based Detection**
  - Statistical analysis using radial distance from normal values
  - Threshold: distance from center point
  - Fast and interpretable results

**Alarm Notifications**
  When anomalies are detected, HTTP POST notifications are sent to the configured endpoint with payload::

    {
      "ts": "2024-01-01T12:00:00Z",
      "anomaly_score": 0.85,
      "vitals": {
        "heart_rate": 95.5,
        "oxygen_saturation": 88.2,
        "breathing_rate": 22.1,
        "blood_pressure_systolic": 140.3,
        "blood_pressure_diastolic": 85.7,
        "body_temperature": 37.8
      }
    }

Docker Deployment
:::::::::::::::::

1. **Using Makefile commands (recommended)**::

    $ make docker-build
    $ make docker-run

2. **Using Docker directly**::

    $ docker build -t health-sensor-simulator .
    $ docker run -p 8000:8000 health-sensor-simulator


Development & Testing
:::::::::::::::::::::

Running Tests
+++++++++++++

1. **Run all tests**::

    $ make test

2. **Run tests with coverage report**::

    $ make test-coverage

3. **Run tests manually with pytest**::

    $ pytest tests/ -v

Development Setup
+++++++++++++++++

1. **Install development dependencies**::

    $ make install-dev

   This includes:
   
   - pytest for testing
   - coverage for test coverage  
   - httpx for async HTTP testing
   - All documentation tools

Building Documentation
++++++++++++++++++++++

1. **Build HTML documentation**::

    $ make docs-html

2. **Build PDF documentation** (requires LaTeX)::

    $ make docs-pdf

3. **Clean documentation build files**::

    $ make docs-clean

You can find the built documentation in the folder ``docs/build/html``.