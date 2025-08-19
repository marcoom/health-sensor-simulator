Configuration Management
========================

The Health Sensor Simulator provides flexible configuration management through environment variables, ``.env`` files, and default values, supporting different deployment environments and use cases.

Configuration Precedence
-------------------------

The application follows a clear configuration precedence hierarchy:

1. **Environment Variables** (highest priority)
2. **``.env`` file** (middle priority)  
3. **Default values in code** (lowest priority)

This allows for flexible deployment scenarios where production environment variables can override development ``.env`` file settings.

Environment Variables Reference
--------------------------------

Core Application Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 15 15 40
   :header-rows: 1

   * - Variable
     - Default
     - Type
     - Description
   * - ``PROJECT_NAME``
     - ``Health Sensor Simulator``
     - String
     - Application display name
   * - ``PROJECT_SLUG``
     - ``health_sensor_simulator``
     - String
     - Application identifier
   * - ``DEBUG``
     - ``True``
     - Boolean
     - Enable debug mode
   * - ``API_STR``
     - ``/api/v1``
     - String
     - API base path prefix

Logging Configuration
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 15 15 40
   :header-rows: 1

   * - Variable
     - Default
     - Type
     - Description
   * - ``LOG_LEVEL``
     - ``INFO``
     - String
     - Logging level (``DEBUG``, ``INFO``, ``WARNING``)

Server Configuration
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 15 15 40
   :header-rows: 1

   * - Variable
     - Default
     - Type
     - Description
   * - ``FASTAPI_HOST``
     - ``0.0.0.0``
     - String
     - FastAPI server bind address
   * - ``FASTAPI_PORT``
     - ``8000``
     - Integer
     - FastAPI server port
   * - ``STREAMLIT_HOST``
     - ``0.0.0.0``
     - String
     - Streamlit server bind address
   * - ``STREAMLIT_PORT``
     - ``8501``
     - Integer
     - Streamlit server port
   * - ``DATA_GENERATION_INTERVAL_SECONDS``
     - ``5``
     - Integer
     - Health data auto-refresh interval

Anomaly Detection Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 15 15 40
   :header-rows: 1

   * - Variable
     - Default
     - Type
     - Description
   * - ``ANOMALY_DETECTION_METHOD``
     - ``DISTANCE``
     - String
     - Detection method (``DISTANCE`` or ``EIF``)
   * - ``EIF_THRESHOLD``
     - ``0.4``
     - Float
     - EIF anomaly probability threshold (0.0-1.0)
   * - ``DISTANCE_THRESHOLD``
     - ``3.8``
     - Float
     - Distance-based detection threshold

Alarm System Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 15 15 40
   :header-rows: 1

   * - Variable
     - Default
     - Type
     - Description
   * - ``ALARM_ENDPOINT_URL``
     - ``None``
     - String
     - HTTP endpoint URL for anomaly notifications

Configuration Files
--------------------

.env File
~~~~~~~~~

Create a ``.env`` file in the project root directory for local development::

    # Health Sensor Simulator Environment Configuration
    
    # Logging
    LOG_LEVEL=DEBUG
    
    # Server Configuration
    FASTAPI_PORT=8000
    STREAMLIT_PORT=8501
    
    # Anomaly Detection
    ANOMALY_DETECTION_METHOD=EIF
    EIF_THRESHOLD=0.4
    DISTANCE_THRESHOLD=3.8
    
    # Alarm System
    ALARM_ENDPOINT_URL=http://localhost:8080/alerts

Production Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

For production deployment, set environment variables directly::

    export LOG_LEVEL=INFO
    export ANOMALY_DETECTION_METHOD=EIF
    export EIF_THRESHOLD=0.3
    export ALARM_ENDPOINT_URL=https://alerts.production.com/webhooks/health

Docker Configuration
~~~~~~~~~~~~~~~~~~~~

Use environment variables in Docker deployment::

    docker run -e LOG_LEVEL=INFO \
               -e ANOMALY_DETECTION_METHOD=EIF \
               -e ALARM_ENDPOINT_URL=https://alerts.example.com/webhooks \
               -p 8000:8000 \
               health-sensor-simulator

Configuration Validation
-------------------------

The application validates all configuration values at startup:

- **Log levels** must be one of: ``DEBUG``, ``INFO``, ``WARNING``
- **Anomaly detection methods** must be one of: ``DISTANCE``, ``EIF``
- **Thresholds** must be valid numeric values
- **URLs** are validated for proper format when provided

Invalid configurations will cause the application to fail at startup with descriptive error messages.

Development vs Production
-------------------------

Development Setup
~~~~~~~~~~~~~~~~~

For local development, use a ``.env`` file with debug settings::

    LOG_LEVEL=DEBUG
    DEBUG=True
    ANOMALY_DETECTION_METHOD=DISTANCE
    ALARM_ENDPOINT_URL=http://localhost:8080/alerts

Production Setup
~~~~~~~~~~~~~~~~

For production, use environment variables with appropriate settings::

    LOG_LEVEL=INFO
    DEBUG=False
    ANOMALY_DETECTION_METHOD=EIF
    EIF_THRESHOLD=0.3
    ALARM_ENDPOINT_URL=https://production-alerts.example.com/api/alerts

Configuration Best Practices
-----------------------------

1. **Never commit secrets** to version control - use environment variables for sensitive data
2. **Use .env files** for local development convenience
3. **Set explicit values** in production environments rather than relying on defaults
4. **Validate configuration** during application startup
5. **Document all variables** with their purpose and valid values
6. **Use appropriate log levels** for different environments (DEBUG for dev, INFO for prod)