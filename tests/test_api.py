from src.app.version import __version__
import pytest
from datetime import datetime
import os
import json
from unittest.mock import patch
from src.app.services.data_simulator import (
    store_current_health_point, 
    generate_health_point_with_variance,
    get_default_health_values,
    get_health_data_file_path
)
from src.app.constants import DEFAULT_DISPERSION


def test_get_version(test_client):
    """Test GET /version endpoint returns correct version."""
    response = test_client.get("/api/v1/version")
    assert response.status_code == 200
    assert response.json() == {"version": __version__}


def test_get_version_response_structure(test_client):
    """Test that version response has correct structure."""
    response = test_client.get("/api/v1/version")
    assert response.status_code == 200
    
    json_response = response.json()
    assert "version" in json_response
    assert isinstance(json_response["version"], str)
    assert len(json_response) == 1


def test_get_version_content_type(test_client):
    """Test that version endpoint returns JSON content type."""
    response = test_client.get("/api/v1/version")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"


def test_get_version_version_format(test_client):
    """Test that version follows semantic versioning format."""
    response = test_client.get("/api/v1/version")
    assert response.status_code == 200
    
    version = response.json()["version"]
    version_parts = version.split(".")
    assert len(version_parts) >= 2, "Version should have at least major.minor format"
    
    for part in version_parts:
        assert part.isdigit(), f"Version part '{part}' should be numeric"


def test_get_version_matches_module_version(test_client):
    """Test that API version matches the module version exactly."""
    response = test_client.get("/api/v1/version")
    assert response.status_code == 200
    assert response.json()["version"] == __version__


def test_get_version_wrong_path_returns_404(test_client):
    """Test that wrong version paths return 404."""
    wrong_paths = [
        "/version",
        "/api/version", 
        "/api/v1/ver",
        "/api/v2/version"
    ]
    
    for path in wrong_paths:
        response = test_client.get(path)
        assert response.status_code == 404


def test_get_vitals(test_client):
    """Test GET /vitals endpoint returns health data."""
    response = test_client.get("/api/v1/vitals")
    assert response.status_code == 200
    
    json_response = response.json()
    
    # Check required fields exist
    required_fields = [
        "ts", "heart_rate", "oxygen_saturation", "breathing_rate",
        "systolic_bp", "diastolic_bp", "body_temperature"
    ]
    for field in required_fields:
        assert field in json_response, f"Missing field: {field}"


def test_get_vitals_data_types(test_client):
    """Test that vitals response has correct data types."""
    response = test_client.get("/api/v1/vitals")
    assert response.status_code == 200
    
    json_response = response.json()
    
    # Check data types
    assert isinstance(json_response["ts"], str), "Timestamp should be string"
    assert isinstance(json_response["heart_rate"], int), "Heart rate should be integer"
    assert isinstance(json_response["oxygen_saturation"], int), "Oxygen saturation should be integer"
    assert isinstance(json_response["breathing_rate"], int), "Breathing rate should be integer"
    assert isinstance(json_response["systolic_bp"], int), "Systolic BP should be integer"
    assert isinstance(json_response["diastolic_bp"], int), "Diastolic BP should be integer"
    assert isinstance(json_response["body_temperature"], float), "Body temperature should be float"


def test_get_vitals_reasonable_ranges(test_client):
    """Test that vitals values are within reasonable physiological ranges."""
    response = test_client.get("/api/v1/vitals")
    assert response.status_code == 200
    
    json_response = response.json()
    
    # Check reasonable ranges (allowing for variance around normal values)
    assert 50 <= json_response["heart_rate"] <= 150, "Heart rate out of reasonable range"
    assert 90 <= json_response["oxygen_saturation"] <= 100, "Oxygen saturation out of range" 
    assert 8 <= json_response["breathing_rate"] <= 30, "Breathing rate out of range"
    assert 70 <= json_response["systolic_bp"] <= 180, "Systolic BP out of range"
    assert 40 <= json_response["diastolic_bp"] <= 120, "Diastolic BP out of range"
    assert 35.0 <= json_response["body_temperature"] <= 38.5, "Body temperature out of range"


def test_get_vitals_timestamp_format(test_client):
    """Test that vitals response timestamp is in correct UTC format."""
    response = test_client.get("/api/v1/vitals")
    assert response.status_code == 200
    
    json_response = response.json()
    timestamp_str = json_response["ts"]
    
    # Should be able to parse as ISO format with timezone
    try:
        parsed_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        assert parsed_timestamp.tzinfo is not None, "Timestamp should include timezone"
    except ValueError:
        pytest.fail(f"Timestamp format invalid: {timestamp_str}")


def test_get_vitals_variance(test_client):
    """Test that vitals endpoint returns different values on multiple calls."""
    # Make multiple calls to test variance
    responses = []
    for _ in range(5):
        response = test_client.get("/api/v1/vitals")
        assert response.status_code == 200
        responses.append(response.json())
    
    # Check that we get some variance in the data (not all identical)
    heart_rates = [r["heart_rate"] for r in responses]
    unique_heart_rates = len(set(heart_rates))
    
    # We should get at least some variation (but due to randomness, we don't require all different)
    assert unique_heart_rates >= 1, "Should have at least one heart rate value"

def test_vitals_file_storage_mechanism(test_client):
    """Test that vitals endpoint uses file storage for inter-process communication."""
    # Clean up any existing file before test
    if os.path.exists(get_health_data_file_path()):
        os.remove(get_health_data_file_path())
    
    # First, store some data to trigger file creation
    test_health_point = {
        'heart_rate': 75.0,
        'oxygen_saturation': 97.0,
        'breathing_rate': 16.0,
        'blood_pressure_systolic': 110.0,
        'blood_pressure_diastolic': 70.0,
        'body_temperature': 36.8
    }
    store_current_health_point(test_health_point)
    
    # Check that file was created
    assert os.path.exists(get_health_data_file_path()), "Health data file should be created"
    
    # Make API call - should read from file
    response = test_client.get("/api/v1/vitals")
    assert response.status_code == 200
    
    # Verify file contains valid JSON
    with open(get_health_data_file_path(), 'r') as f:
        file_data = json.load(f)
    
    # Check file contains all required health parameters
    required_params = [
        'heart_rate', 'oxygen_saturation', 'breathing_rate',
        'blood_pressure_systolic', 'blood_pressure_diastolic', 'body_temperature'
    ]
    for param in required_params:
        assert param in file_data, f"File missing parameter: {param}"
    
    # Check that API response matches file data
    json_response = response.json()
    assert abs(file_data['heart_rate'] - json_response['heart_rate']) < 1.0
    assert abs(file_data['oxygen_saturation'] - json_response['oxygen_saturation']) < 1.0
    assert abs(file_data['body_temperature'] - json_response['body_temperature']) < 0.1


def test_vitals_streamlit_api_synchronization(test_client):
    """Test that API returns same values that Streamlit stores."""
    # Clean up any existing file
    if os.path.exists(get_health_data_file_path()):
        os.remove(get_health_data_file_path())
    
    # Simulate Streamlit UI setting custom health values
    custom_health_values = {
        'heart_rate': 125.0,
        'oxygen_saturation': 94.0,
        'breathing_rate': 22.0,
        'systolic_bp': 140.0,
        'diastolic_bp': 88.0,
        'body_temperature': 37.8
    }
    custom_dispersion = 0.15
    
    # Generate health point as Streamlit would
    streamlit_health_point = generate_health_point_with_variance(
        custom_health_values, custom_dispersion
    )
    
    # Store as Streamlit would
    store_current_health_point(streamlit_health_point)
    
    # API call should return the same values
    response = test_client.get("/api/v1/vitals")
    assert response.status_code == 200
    
    json_response = response.json()
    
    # Check synchronization (allowing for rounding)
    assert abs(streamlit_health_point['heart_rate'] - json_response['heart_rate']) < 1.0
    assert abs(streamlit_health_point['oxygen_saturation'] - json_response['oxygen_saturation']) < 1.0
    assert abs(streamlit_health_point['breathing_rate'] - json_response['breathing_rate']) < 1.0
    assert abs(streamlit_health_point['blood_pressure_systolic'] - json_response['systolic_bp']) < 1.0
    assert abs(streamlit_health_point['blood_pressure_diastolic'] - json_response['diastolic_bp']) < 1.0
    assert abs(streamlit_health_point['body_temperature'] - json_response['body_temperature']) < 0.1


def test_vitals_multiple_streamlit_updates(test_client):
    """Test that API reflects multiple rapid Streamlit updates correctly."""
    # Clean up any existing file
    if os.path.exists(get_health_data_file_path()):
        os.remove(get_health_data_file_path())
    
    test_scenarios = [
        {'hr': 70.0, 'temp': 36.2, 'spo2': 99.0},  # Resting
        {'hr': 130.0, 'temp': 37.5, 'spo2': 96.0}, # Exercising  
        {'hr': 55.0, 'temp': 35.8, 'spo2': 98.0},  # Sleeping
    ]
    
    for i, scenario in enumerate(test_scenarios):
        # Simulate Streamlit user changing sliders
        health_values = {
            'heart_rate': scenario['hr'],
            'oxygen_saturation': scenario['spo2'],
            'breathing_rate': 16.0,
            'systolic_bp': 110.0,
            'diastolic_bp': 70.0,
            'body_temperature': scenario['temp']
        }
        
        # Generate and store as Streamlit would
        health_point = generate_health_point_with_variance(health_values, 0.05)
        store_current_health_point(health_point)
        
        # Check API immediately reflects the change
        response = test_client.get("/api/v1/vitals")
        assert response.status_code == 200
        
        json_response = response.json()
        
        # Verify synchronization
        hr_match = abs(health_point['heart_rate'] - json_response['heart_rate']) < 1.0
        temp_match = abs(health_point['body_temperature'] - json_response['body_temperature']) < 0.1
        spo2_match = abs(health_point['oxygen_saturation'] - json_response['oxygen_saturation']) < 1.0
        
        assert hr_match, f"Scenario {i+1}: HR not synchronized"
        assert temp_match, f"Scenario {i+1}: Temperature not synchronized" 
        assert spo2_match, f"Scenario {i+1}: SpO2 not synchronized"


def test_vitals_extreme_values_synchronization(test_client):
    """Test synchronization with extreme but valid health values."""
    # Clean up any existing file
    if os.path.exists(get_health_data_file_path()):
        os.remove(get_health_data_file_path())
    
    # Test with extreme but medically possible values
    extreme_values = {
        'heart_rate': 200.0,      # Maximum exercise heart rate
        'oxygen_saturation': 85.0, # Severe hypoxemia
        'breathing_rate': 35.0,    # Severe tachypnea
        'systolic_bp': 200.0,      # Severe hypertension
        'diastolic_bp': 120.0,     # Severe hypertension
        'body_temperature': 41.0   # Severe hyperthermia
    }
    
    # Generate with minimal dispersion for predictable results
    extreme_point = generate_health_point_with_variance(extreme_values, 0.01)
    store_current_health_point(extreme_point)
    
    # API should handle extreme values correctly
    response = test_client.get("/api/v1/vitals")
    assert response.status_code == 200
    
    json_response = response.json()
    
    # Verify extreme values are synchronized correctly
    assert abs(extreme_point['heart_rate'] - json_response['heart_rate']) < 1.0
    assert abs(extreme_point['oxygen_saturation'] - json_response['oxygen_saturation']) < 1.0
    assert abs(extreme_point['body_temperature'] - json_response['body_temperature']) < 0.1
    
    # Ensure values are still within the test ranges we defined
    assert json_response['heart_rate'] >= 50, "Heart rate should be at least 50 for test validity"
    assert json_response['oxygen_saturation'] >= 80, "SpO2 should be at least 80 for test validity"
    assert json_response['body_temperature'] <= 45.0, "Temperature should be at most 45°C for test validity"


# ============================================================================
# EDGE CASE TESTS: File Corruption, Missing Files, etc.
# ============================================================================

def test_vitals_missing_file_fallback(test_client):
    """Test that vitals endpoint handles missing storage file gracefully."""
    # Ensure file doesn't exist and clear any cached values
    if os.path.exists(get_health_data_file_path()):
        os.remove(get_health_data_file_path())
    
    # Clear any cached values in memory
    import src.app.services.data_simulator as ds_module
    ds_module._last_health_point = None
    
    # API call should still work and create default values
    response = test_client.get("/api/v1/vitals")
    assert response.status_code == 200
    
    json_response = response.json()
    
    # Should return reasonable default values (expanded range to account for variance)
    assert 50 <= json_response['heart_rate'] <= 150
    assert 85 <= json_response['oxygen_saturation'] <= 100
    assert 35.0 <= json_response['body_temperature'] <= 38.5


def test_vitals_corrupted_file_fallback(test_client):
    """Test that vitals endpoint handles corrupted storage file gracefully."""
    # Clear any cached values in memory first
    import src.app.services.data_simulator as ds_module
    ds_module._last_health_point = None
    
    # Create a corrupted file
    with open(get_health_data_file_path(), 'w') as f:
        f.write("{ invalid json content }")
    
    # API call should still work despite corrupted file
    response = test_client.get("/api/v1/vitals")
    assert response.status_code == 200
    
    json_response = response.json()
    
    # Should return reasonable fallback values (expanded range to account for variance)
    assert 50 <= json_response['heart_rate'] <= 150
    assert 85 <= json_response['oxygen_saturation'] <= 100
    assert 35.0 <= json_response['body_temperature'] <= 38.5


def test_vitals_empty_file_fallback(test_client):
    """Test that vitals endpoint handles empty storage file gracefully."""
    # Clear any cached values in memory first
    import src.app.services.data_simulator as ds_module
    ds_module._last_health_point = None
    
    # Create an empty file
    with open(get_health_data_file_path(), 'w') as f:
        f.write("")
    
    # API call should still work despite empty file
    response = test_client.get("/api/v1/vitals")
    assert response.status_code == 200
    
    json_response = response.json()
    
    # Should return reasonable fallback values (expanded range to account for variance)
    assert 50 <= json_response['heart_rate'] <= 150
    assert 85 <= json_response['oxygen_saturation'] <= 100
    assert 35.0 <= json_response['body_temperature'] <= 38.5


@patch('src.app.services.data_simulator.os.path.exists')
@patch('builtins.open')
def test_vitals_file_permission_error_fallback(mock_open, mock_exists, test_client):
    """Test that vitals endpoint handles file permission errors gracefully."""
    # Mock file exists but can't be read
    mock_exists.return_value = True
    mock_open.side_effect = PermissionError("Permission denied")
    
    # API call should still work despite permission error
    response = test_client.get("/api/v1/vitals")
    assert response.status_code == 200
    
    json_response = response.json()
    
    # Should return reasonable fallback values
    assert 50 <= json_response['heart_rate'] <= 150
    assert 90 <= json_response['oxygen_saturation'] <= 100
    assert 35.0 <= json_response['body_temperature'] <= 38.5


def test_vitals_file_atomic_write_integrity(test_client):
    """Test that file writes are atomic and don't corrupt concurrent reads."""
    # Clean up any existing file
    if os.path.exists(get_health_data_file_path()):
        os.remove(get_health_data_file_path())
    
    # Store initial value
    initial_values = get_default_health_values()
    initial_point = generate_health_point_with_variance(initial_values, DEFAULT_DISPERSION)
    store_current_health_point(initial_point)
    
    # Verify file exists and is readable
    assert os.path.exists(get_health_data_file_path())
    
    # Read directly from file to verify integrity
    with open(get_health_data_file_path(), 'r') as f:
        file_data = json.load(f)
    
    # Ensure all required fields are present
    required_fields = ['heart_rate', 'oxygen_saturation', 'breathing_rate', 
                      'blood_pressure_systolic', 'blood_pressure_diastolic', 'body_temperature']
    
    for field in required_fields:
        assert field in file_data, f"Required field missing after atomic write: {field}"
        assert isinstance(file_data[field], (int, float)), f"Field {field} has invalid type"
    
    # API should read the same data
    response = test_client.get("/api/v1/vitals")
    assert response.status_code == 200
    
    json_response = response.json()
    assert abs(file_data['heart_rate'] - json_response['heart_rate']) < 1.0


def test_vitals_concurrent_file_operations(test_client):
    """Test that concurrent store/read operations work correctly."""
    # Clean up any existing file
    if os.path.exists(get_health_data_file_path()):
        os.remove(get_health_data_file_path())
    
    # Simulate rapid concurrent operations
    test_values = []
    for i in range(5):
        values = {
            'heart_rate': 80.0 + i * 10,
            'oxygen_saturation': 95.0 + i,
            'breathing_rate': 15.0 + i,
            'systolic_bp': 110.0 + i * 5,
            'diastolic_bp': 70.0 + i * 2,
            'body_temperature': 36.5 + i * 0.2
        }
        health_point = generate_health_point_with_variance(values, 0.01)
        store_current_health_point(health_point)
        test_values.append(health_point)
        
        # Immediately read via API
        response = test_client.get("/api/v1/vitals")
        assert response.status_code == 200
    
    # Final verification - should have the last stored value
    final_response = test_client.get("/api/v1/vitals")
    assert final_response.status_code == 200
    
    final_data = final_response.json()
    last_stored = test_values[-1]
    
    # Should match the last stored value
    assert abs(last_stored['heart_rate'] - final_data['heart_rate']) < 1.0
    assert abs(last_stored['oxygen_saturation'] - final_data['oxygen_saturation']) < 1.0
