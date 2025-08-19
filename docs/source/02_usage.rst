Usage
=====

**[COMPLETE]** **Current Status**: Fully functional health sensor simulator with FastAPI backend, Streamlit UI, and comprehensive inter-process communication for synchronized health data.

Current API Endpoints
---------------------

- ``GET /api/v1/version`` - Returns the service version
- ``GET /api/v1/vitals`` - Returns latest health readings (synchronized with Streamlit UI via file-based IPC)

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

Environment Variables
:::::::::::::::::::::

.. list-table:: Environment Variables
   :widths: 15 25 50
   :header-rows: 1

   * - Variable
     - Sample Value
     - Description
   * - ALARM_ENDPOINT_URL
     - ``https://api.example.com/alarms``
     - URL where anomaly POST notifications should be sent
   * - MODE
     - ``DEV``, ``TEST``, ``PROD``
     - Deployment environment configuration (optional)

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