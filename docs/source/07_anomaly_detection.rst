Anomaly Detection & Alarm System
==================================

The Health Sensor Simulator implements a sophisticated anomaly detection system with two complementary methods and an intelligent alarm notification system for real-time health monitoring.

Detection Methods Overview
---------------------------

The system supports two anomaly detection approaches that can be selected via configuration:

1. **Extended Isolation Forest (EIF)** - Machine learning-based detection
2. **Distance-based Detection** - Statistical analysis approach

Both methods analyze the same health parameters but use different algorithms to identify anomalous patterns in vital signs.

Health Parameters Monitored
----------------------------

The system monitors six critical health parameters:

.. list-table:: Health Parameter Specifications
   :widths: 25 15 15 15 15 15
   :header-rows: 1

   * - Parameter
     - Unit
     - Normal Min
     - Normal Max
     - Normal Mean
     - Std Dev
   * - Heart Rate
     - bpm
     - 60.0
     - 100.0
     - 80.0
     - 6.7
   * - Oxygen Saturation
     - %
     - 95.0
     - 100.0
     - 97.5
     - 0.8
   * - Breathing Rate
     - breaths/min
     - 12.0
     - 20.0
     - 16.0
     - 1.3
   * - Systolic Blood Pressure
     - mmHg
     - 90.0
     - 120.0
     - 105.0
     - 5.0
   * - Diastolic Blood Pressure
     - mmHg
     - 60.0
     - 80.0
     - 70.0
     - 3.3
   * - Body Temperature
     - °C
     - 36.1
     - 37.2
     - 36.7
     - 0.2

Extended Isolation Forest (EIF)
--------------------------------

Machine Learning Approach
~~~~~~~~~~~~~~~~~~~~~~~~~~

The EIF method uses a pre-trained Extended Isolation Forest model to detect complex patterns and multivariate anomalies in health data.

**Key Features:**
- **Advanced Pattern Recognition**: Detects subtle anomalies that statistical methods might miss
- **Multivariate Analysis**: Considers relationships between multiple health parameters simultaneously
- **Pre-trained Model**: Uses ``src/models/eif.joblib`` trained on historical health data
- **Probability-based Scoring**: Returns anomaly probability scores (0.0-1.0)

**Configuration:**

.. code-block:: bash

   ANOMALY_DETECTION_METHOD=EIF
   EIF_THRESHOLD=0.4

**Model Details:**
- **Algorithm**: Extended Isolation Forest with hyperplane cuts
- **Library**: ``isotree`` (optimized implementation)
- **Features**: All 6 health parameters
- **Training**: Supervised learning on labeled health datasets
- **Output**: Anomaly probability score (higher = more anomalous)

**Advantages:**
- Superior detection of complex, multivariate anomalies
- Learns from historical patterns
- Robust to noise and normal variations
- Industry-standard machine learning approach

**Limitations:**
- Requires pre-trained model
- Less interpretable than distance-based method
- Computationally more intensive

Distance-based Detection
------------------------

Statistical Approach
~~~~~~~~~~~~~~~~~~~~~

The distance-based method calculates the radial distance of current health readings from the center point (normal resting values).

**Key Features:**
- **Fast Computation**: Real-time statistical analysis
- **Interpretable Results**: Clear mathematical relationship to normal values
- **No Training Required**: Uses predefined normal ranges
- **Distance-based Scoring**: Measures deviation from healthy baseline

**Configuration:**

.. code-block:: bash

   ANOMALY_DETECTION_METHOD=DISTANCE
   DISTANCE_THRESHOLD=3.8

**Algorithm:**
1. Calculate center point using mean resting values for each parameter
2. Compute radial distance from current readings to center point
3. Compare distance to threshold
4. Generate anomaly score based on distance magnitude

**Advantages:**
- Fast and lightweight
- Highly interpretable
- No model training required
- Stable and predictable behavior

**Limitations:**
- May miss complex multivariate patterns
- Less sophisticated than ML approaches
- Fixed normal ranges may not adapt to individual variations

Threshold Configuration
-----------------------

EIF Threshold
~~~~~~~~~~~~~

The EIF threshold determines the anomaly probability above which readings are flagged:

.. code-block:: bash

   EIF_THRESHOLD=0.4  # 0.0 (never anomaly) to 1.0 (always anomaly)

**Threshold Guidelines:**
- **0.2-0.3**: Very sensitive, catches subtle anomalies
- **0.4-0.5**: Balanced sensitivity (recommended)
- **0.6-0.8**: Conservative, only obvious anomalies

Distance Threshold
~~~~~~~~~~~~~~~~~~

The distance threshold sets the radial distance limit for normal readings:

.. code-block:: bash

   DISTANCE_THRESHOLD=3.8  # Distance units from center point

**Threshold Guidelines:**
- **2.0-3.0**: High sensitivity
- **3.5-4.0**: Moderate sensitivity (recommended)
- **4.5-6.0**: Low sensitivity, only severe anomalies

Alarm Notification System
--------------------------

Automatic Notifications
~~~~~~~~~~~~~~~~~~~~~~~

When anomalies are detected, the system automatically sends HTTP POST notifications to configured endpoints.

**Configuration:**

.. code-block:: bash

   ALARM_ENDPOINT_URL=http://localhost:8080/alerts

**Notification Payload:**

.. code-block:: json

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

**Payload Fields:**
- ``ts``: ISO 8601 timestamp of anomaly detection
- ``anomaly_score``: Calculated anomaly score (0.0-1.0)
- ``vitals``: Complete health parameter values at time of anomaly

Error Handling
~~~~~~~~~~~~~~

The alarm system includes robust error handling:

- **Connection Errors**: Logged as debug messages (no alarm server running)
- **Timeout Handling**: 10-second timeout with graceful fallback
- **HTTP Errors**: Non-200 status codes logged with details
- **Retry Logic**: Single retry attempt for failed requests
- **Graceful Degradation**: Anomaly detection continues even if alarms fail

Integration Examples
--------------------

Webhook Endpoint
~~~~~~~~~~~~~~~~

Example webhook server to receive alarm notifications::

    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    
    @app.route('/alerts', methods=['POST'])
    def receive_alarm():
        data = request.get_json()
        
        # Process anomaly data
        timestamp = data['ts']
        score = data['anomaly_score']
        vitals = data['vitals']
        
        # Your alarm handling logic here
        print(f"ANOMALY DETECTED at {timestamp}")
        print(f"Score: {score}, Vitals: {vitals}")
        
        return jsonify({"status": "received"})

Slack Integration
~~~~~~~~~~~~~~~~~

Example Slack webhook integration::

    import requests
    import json
    
    def forward_to_slack(anomaly_data):
        slack_webhook = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
        
        message = {
            "text": f"🚨 Health Anomaly Detected!",
            "attachments": [{
                "color": "danger",
                "fields": [
                    {"title": "Anomaly Score", "value": str(anomaly_data['anomaly_score']), "short": True},
                    {"title": "Time", "value": anomaly_data['ts'], "short": True},
                    {"title": "Heart Rate", "value": f"{anomaly_data['vitals']['heart_rate']} bpm", "short": True},
                    {"title": "Oxygen Sat", "value": f"{anomaly_data['vitals']['oxygen_saturation']}%", "short": True}
                ]
            }]
        }
        
        requests.post(slack_webhook, json=message)

Model Management
----------------

EIF Model Training
~~~~~~~~~~~~~~~~~~

The EIF model can be retrained with new data:

1. **Prepare Training Data**: Health parameter datasets with normal/anomaly labels
2. **Train Model**: Use ``notebooks/02_anomaly_detection_model.ipynb``
3. **Validate Performance**: Test on holdout dataset
4. **Export Model**: Save to ``src/models/eif.joblib``
5. **Deploy**: Restart application to load new model

**Model Requirements:**
- Feature names must match health parameter names exactly
- Model must return probability scores (0.0-1.0)
- Compatible with ``isotree`` library interface

Model Validation
~~~~~~~~~~~~~~~~~

Validate model performance before deployment::

    from src.app.services.anomaly_detector import _load_eif_model
    
    # Load and test model
    model = _load_eif_model()
    if model:
        print("Model loaded successfully")
        print(f"Features: {model['feature_names']}")
        print(f"Threshold: {model['threshold']}")
    else:
        print("Model loading failed")

Performance Considerations
--------------------------

EIF Performance
~~~~~~~~~~~~~~~

- **Model Loading**: Cached after first load for performance
- **Prediction Time**: ~1-5ms per health point
- **Memory Usage**: ~10-50MB for typical models
- **Startup Time**: 100-500ms for model loading

Distance Performance
~~~~~~~~~~~~~~~~~~~~

- **Calculation Time**: <1ms per health point
- **Memory Usage**: Minimal (no model storage)
- **Startup Time**: Instant

**Recommendation**: Use EIF for accuracy, Distance for speed and simplicity.

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Model Loading Failures:**
- Verify ``src/models/eif.joblib`` exists
- Check file permissions
- Ensure ``isotree`` and ``joblib`` are installed
- Validate model format and feature names

**Alarm Delivery Issues:**
- Verify ``ALARM_ENDPOINT_URL`` configuration
- Check network connectivity to alarm endpoint
- Monitor application logs for error messages
- Test endpoint manually with curl

**False Positives/Negatives:**
- Adjust detection thresholds
- Review health parameter normal ranges
- Consider retraining EIF model with more data
- Validate input data quality

Debug Logging
~~~~~~~~~~~~~

Enable debug logging for detailed information::

    LOG_LEVEL=DEBUG

This provides detailed logs for:
- Model loading and validation
- Anomaly detection calculations
- Alarm notification attempts
- Configuration validation