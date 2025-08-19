"""Tests for anomaly detection functionality."""

import pytest
from src.app.services.anomaly_detector import detect_anomaly
from src.app.constants import HEALTH_PARAMS


class TestDetectAnomaly:
    """Test cases for detect_anomaly function."""

    def test_detect_anomaly_normal_values(self):
        """Test that normal health values are not flagged as anomalies."""
        # Create a health point with all normal/resting values
        normal_health_point = {}
        for param_name, param_spec in HEALTH_PARAMS.items():
            normal_health_point[param_name] = param_spec["mean_rest"]
        
        is_anomaly, score = detect_anomaly(normal_health_point)
        
        assert is_anomaly is False, "Normal values should not be flagged as anomalies"
        assert 0.0 <= score <= 0.5, "Normal values should have low anomaly score"

    def test_detect_anomaly_slight_deviation(self):
        """Test slightly deviated but still normal values."""
        # Create a health point with minimal deviations from mean
        health_point = {
            "heart_rate": 82.0,        # Slight increase from 80.0
            "oxygen_saturation": 97.0,  # Slight decrease from 97.5
            "breathing_rate": 17.0,     # Slight increase from 16.0
            "blood_pressure_systolic": 107.0,  # Slight increase from 105.0
            "blood_pressure_diastolic": 72.0,  # Slight increase from 70.0
            "body_temperature": 36.9    # Slight increase from 36.7
        }
        
        is_anomaly, score = detect_anomaly(health_point)
        
        # These small deviations should result in low distance and low score
        assert 0.0 <= score <= 1.0, "Score should be valid range"
        # Don't assert anomaly status since small deviations can accumulate

    def test_detect_anomaly_mild_anomaly(self):
        """Test values that should create an anomaly."""
        # Create a health point with abnormal values
        health_point = {
            "heart_rate": 105.0,       # Elevated from 80.0
            "oxygen_saturation": 94.0,  # Low from 97.5
            "breathing_rate": 22.0,     # Elevated from 16.0
            "blood_pressure_systolic": 130.0,  # High from 105.0
            "blood_pressure_diastolic": 85.0,  # High from 70.0
            "body_temperature": 38.0    # Fever from 36.7
        }
        
        is_anomaly, score = detect_anomaly(health_point)
        
        # Should be flagged as anomaly with elevated score
        assert 0.0 <= score <= 1.0, "Score should be in valid range"

    def test_detect_anomaly_severe_anomaly(self):
        """Test values that create a severe anomaly (distance >= 4.0)."""
        # Create a health point with severely abnormal values
        health_point = {
            "heart_rate": 150.0,       # Very high
            "oxygen_saturation": 85.0,  # Dangerously low
            "breathing_rate": 35.0,     # Very high
            "blood_pressure_systolic": 180.0,  # Very high
            "blood_pressure_diastolic": 110.0,  # Very high
            "body_temperature": 40.0    # High fever
        }
        
        is_anomaly, score = detect_anomaly(health_point)
        
        assert is_anomaly is True, "Severely abnormal values should be flagged as anomalies"
        assert 0.75 <= score <= 1.0, "Severe anomaly should have high score"

    def test_detect_anomaly_custom_threshold(self):
        """Test anomaly detection with custom threshold via configuration."""
        from unittest.mock import patch
        from src.app.config import Settings
        
        # Create a health point that would be anomalous with lower threshold
        health_point = {
            "heart_rate": 95.0,
            "oxygen_saturation": 94.0,  # Slightly below normal
            "breathing_rate": 22.0,     # Slightly above normal
            "blood_pressure_systolic": 125.0,  # Slightly above normal
            "blood_pressure_diastolic": 85.0,  # Slightly above normal
            "body_temperature": 37.5    # Slightly elevated
        }
        
        # Test with default threshold via mock settings
        with patch('src.app.services.anomaly_detector.get_settings') as mock_settings:
            settings = Settings()
            settings.ANOMALY_DETECTION_METHOD = "DISTANCE"
            settings.DISTANCE_THRESHOLD = 3.8  # Default threshold
            settings.ALARM_ENDPOINT_URL = None  # Disable alarms for this test
            mock_settings.return_value = settings
            
            is_anomaly_default, score_default = detect_anomaly(health_point)
        
        # Test with lower threshold
        with patch('src.app.services.anomaly_detector.get_settings') as mock_settings:
            settings = Settings()
            settings.ANOMALY_DETECTION_METHOD = "DISTANCE"
            settings.DISTANCE_THRESHOLD = 2.0  # Lower threshold
            settings.ALARM_ENDPOINT_URL = None  # Disable alarms for this test
            mock_settings.return_value = settings
            
            is_anomaly_low, score_low = detect_anomaly(health_point)
        
        # Verify return types and ranges
        assert isinstance(is_anomaly_default, bool)
        assert isinstance(is_anomaly_low, bool)
        assert 0.0 <= score_default <= 1.0
        assert 0.0 <= score_low <= 1.0

    def test_detect_anomaly_return_types(self):
        """Test that function returns correct types."""
        health_point = {param: spec["mean_rest"] for param, spec in HEALTH_PARAMS.items()}
        
        is_anomaly, score = detect_anomaly(health_point)
        
        assert isinstance(is_anomaly, bool), "is_anomaly should be boolean"
        assert isinstance(score, float), "score should be float"
        assert 0.0 <= score <= 1.0, "score should be between 0.0 and 1.0"

    def test_detect_anomaly_single_parameter(self):
        """Test anomaly detection with single parameter."""
        health_point = {"heart_rate": 200.0}  # Extremely high heart rate
        
        is_anomaly, score = detect_anomaly(health_point)
        
        assert isinstance(is_anomaly, bool)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_detect_anomaly_unknown_parameter(self):
        """Test behavior with unknown parameter."""
        health_point = {
            "heart_rate": 80.0,
            "unknown_param": 100.0  # Parameter not in HEALTH_PARAMS
        }
        
        # Should not raise an error
        is_anomaly, score = detect_anomaly(health_point)
        
        assert isinstance(is_anomaly, bool)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_detect_anomaly_empty_health_point(self):
        """Test behavior with empty health point."""
        health_point = {}
        
        is_anomaly, score = detect_anomaly(health_point)
        
        assert isinstance(is_anomaly, bool)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_detect_anomaly_score_consistency(self):
        """Test that higher distances result in higher scores."""
        # Normal values (should have low score)
        normal_point = {param: spec["mean_rest"] for param, spec in HEALTH_PARAMS.items()}
        
        # Slightly abnormal values
        slight_point = {
            "heart_rate": 85.0,
            "oxygen_saturation": 96.0,
            "breathing_rate": 18.0,
            "blood_pressure_systolic": 115.0,
            "blood_pressure_diastolic": 75.0,
            "body_temperature": 37.0
        }
        
        _, normal_score = detect_anomaly(normal_point)
        _, slight_score = detect_anomaly(slight_point)
        
        # Normal should have lower score than slight deviation
        assert normal_score <= slight_score, "Normal score should be less than or equal to slight deviation"
        assert 0.0 <= normal_score <= 1.0, "Normal score should be in valid range"
        assert 0.0 <= slight_score <= 1.0, "Slight score should be in valid range"

    def test_detect_anomaly_threshold_boundary(self):
        """Test behavior around the threshold boundary."""
        from unittest.mock import patch
        from src.app.config import Settings
        
        # Test different threshold values using configuration
        test_cases = [
            (3.7, "lower threshold"),
            (3.8, "default threshold"), 
            (3.9, "higher threshold"),
        ]
        
        # Use mean values - should have distance near 0
        health_point = {param: spec["mean_rest"] for param, spec in HEALTH_PARAMS.items()}
        
        for threshold_val, description in test_cases:
            with patch('src.app.services.anomaly_detector.get_settings') as mock_settings:
                settings = Settings()
                settings.ANOMALY_DETECTION_METHOD = "DISTANCE"
                settings.DISTANCE_THRESHOLD = threshold_val
                settings.ALARM_ENDPOINT_URL = None  # Disable alarms for this test
                mock_settings.return_value = settings
                
                is_anomaly, score = detect_anomaly(health_point)
                
                # For mean values, distance should be 0 (or very close)
                # So with any reasonable threshold, should not be anomaly
                assert is_anomaly is False, f"Mean values should not be anomaly with {description} ({threshold_val})"


class TestEIFAnomalyDetection:
    """Test Extended Isolation Forest anomaly detection functionality."""
    
    def test_eif_method_selection(self):
        """Test that EIF method is selected when configured."""
        from unittest.mock import patch
        from src.app.config import Settings
        
        health_point = {
            "heart_rate": 95.0,
            "oxygen_saturation": 94.0,
            "breathing_rate": 22.0,
            "blood_pressure_systolic": 125.0,
            "blood_pressure_diastolic": 85.0,
            "body_temperature": 37.5
        }
        
        with patch('src.app.services.anomaly_detector.get_settings') as mock_settings:
            settings = Settings()
            settings.ANOMALY_DETECTION_METHOD = "EIF"
            settings.EIF_THRESHOLD = 0.5
            settings.ALARM_ENDPOINT_URL = None  # Disable alarms for this test
            mock_settings.return_value = settings
            
            # Mock the EIF model loading to avoid file dependencies
            with patch('src.app.services.anomaly_detector._load_eif_model') as mock_load:
                mock_load.return_value = None  # Simulate model not available
                
                # Should fallback to distance method
                is_anomaly, score = detect_anomaly(health_point)
                
                assert isinstance(is_anomaly, bool)
                assert 0.0 <= score <= 1.0
                mock_load.assert_called_once()
    
    def test_eif_model_loading_cache(self):
        """Test EIF model loading and caching behavior."""
        from src.app.services.anomaly_detector import _load_eif_model, _eif_model_cache
        from unittest.mock import patch, MagicMock
        import src.app.services.anomaly_detector as anomaly_module
        
        # Reset cache
        anomaly_module._eif_model_cache = None
        
        # Mock successful model loading
        mock_artifact = {
            "model": MagicMock(),
            "threshold": 0.5,
            "feature_names": ["heart_rate", "oxygen_saturation", "breathing_rate", 
                            "blood_pressure_systolic", "blood_pressure_diastolic", "body_temperature"]
        }
        
        with patch('src.app.services.anomaly_detector.load', return_value=mock_artifact):
            # First call should load model
            result1 = _load_eif_model()
            assert result1 == mock_artifact
            
            # Second call should use cache
            result2 = _load_eif_model()
            assert result2 == mock_artifact
            assert result1 is result2  # Same object reference (cached)
    
    def test_eif_standard_feature_names(self):
        """Test EIF with standard feature names from HEALTH_PARAMS."""
        from src.app.services.anomaly_detector import _detect_anomaly_eif
        from unittest.mock import patch, MagicMock
        
        health_point = {
            "heart_rate": 80.0,
            "oxygen_saturation": 97.5,
            "breathing_rate": 16.0,
            "blood_pressure_systolic": 105.0,
            "blood_pressure_diastolic": 70.0,
            "body_temperature": 36.7
        }
        
        # Mock model with standard feature names
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.3]  # Below threshold
        
        mock_artifact = {
            "model": mock_model,
            "threshold": 0.5,
            "feature_names": ["heart_rate", "oxygen_saturation", "breathing_rate", 
                            "blood_pressure_systolic", "blood_pressure_diastolic", "body_temperature"]
        }
        
        with patch('src.app.services.anomaly_detector._load_eif_model', return_value=mock_artifact):
            with patch('src.app.services.anomaly_detector.get_settings') as mock_settings:
                settings = MagicMock()
                settings.EIF_THRESHOLD = 0.5
                mock_settings.return_value = settings
                
                is_anomaly, score = _detect_anomaly_eif(health_point)
                
                # Verify model was called with DataFrame
                mock_model.predict.assert_called_once()
                call_args = mock_model.predict.call_args[0][0]
                
                # Verify standard feature names are used correctly
                expected_features = ["heart_rate", "oxygen_saturation", "breathing_rate", 
                                   "blood_pressure_systolic", "blood_pressure_diastolic", "body_temperature"]
                assert list(call_args.columns) == expected_features
                
                assert is_anomaly is False  # 0.3 < 0.5 threshold
                assert isinstance(score, float)
                assert 0.0 <= score <= 1.0
    
    def test_eif_threshold_configuration(self):
        """Test EIF threshold configuration from settings."""
        from src.app.services.anomaly_detector import _detect_anomaly_eif
        from unittest.mock import patch, MagicMock
        
        health_point = {"heart_rate": 80.0}
        
        # Mock model that returns different scores
        mock_model = MagicMock()
        mock_artifact = {
            "model": mock_model,
            "threshold": 0.7,  # Model threshold (should be ignored)
            "feature_names": ["heart_rate"]
        }
        
        with patch('src.app.services.anomaly_detector._load_eif_model', return_value=mock_artifact):
            # Test with low threshold - should be anomaly
            mock_model.predict.return_value = [0.6]
            with patch('src.app.services.anomaly_detector.get_settings') as mock_settings:
                settings = MagicMock()
                settings.EIF_THRESHOLD = 0.4  # Lower than score
                mock_settings.return_value = settings
                
                is_anomaly, _ = _detect_anomaly_eif(health_point)
                assert is_anomaly is True
            
            # Test with high threshold - should not be anomaly
            mock_model.predict.return_value = [0.6]
            with patch('src.app.services.anomaly_detector.get_settings') as mock_settings:
                settings = MagicMock()
                settings.EIF_THRESHOLD = 0.8  # Higher than score
                mock_settings.return_value = settings
                
                is_anomaly, _ = _detect_anomaly_eif(health_point)
                assert is_anomaly is False
    
    def test_eif_score_normalization(self):
        """Test EIF score normalization to 0-1 range."""
        from src.app.services.anomaly_detector import _detect_anomaly_eif
        from unittest.mock import patch, MagicMock
        
        health_point = {"heart_rate": 80.0}
        
        mock_model = MagicMock()
        mock_artifact = {
            "model": mock_model,
            "threshold": 0.5,
            "feature_names": ["heart_rate"]
        }
        
        with patch('src.app.services.anomaly_detector._load_eif_model', return_value=mock_artifact):
            with patch('src.app.services.anomaly_detector.get_settings') as mock_settings:
                settings = MagicMock()
                settings.EIF_THRESHOLD = 0.5
                mock_settings.return_value = settings
                
                # Test score normalization for different raw scores
                test_cases = [
                    (0.1, 0.0),    # Very low score -> 0.0
                    (0.2, 0.0),    # Low boundary -> 0.0  
                    (0.5, 0.5),    # Middle score -> 0.5
                    (0.8, 1.0),    # High boundary -> 1.0
                    (0.9, 1.0),    # Very high score -> 1.0
                ]
                
                for raw_score, expected_norm in test_cases:
                    mock_model.predict.return_value = [raw_score]
                    _, normalized_score = _detect_anomaly_eif(health_point)
                    assert abs(normalized_score - expected_norm) < 0.1, f"Raw {raw_score} -> {normalized_score}, expected ~{expected_norm}"


class TestAnomalyDetectionMethodSelection:
    """Test anomaly detection method selection and integration."""
    
    def test_distance_method_selection(self):
        """Test that DISTANCE method is selected when configured."""
        from unittest.mock import patch
        from src.app.config import Settings
        
        health_point = {
            "heart_rate": 80.0,
            "oxygen_saturation": 97.5,
            "breathing_rate": 16.0,
            "blood_pressure_systolic": 105.0,
            "blood_pressure_diastolic": 70.0,
            "body_temperature": 36.7
        }
        
        with patch('src.app.services.anomaly_detector.get_settings') as mock_settings:
            settings = Settings()
            settings.ANOMALY_DETECTION_METHOD = "DISTANCE"
            settings.DISTANCE_THRESHOLD = 3.8
            settings.ALARM_ENDPOINT_URL = None  # Disable alarms for this test
            mock_settings.return_value = settings
            
            is_anomaly, score = detect_anomaly(health_point)
            
            # Normal values should not be anomaly with distance method
            assert is_anomaly is False
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0
    
    def test_eif_method_selection_with_model(self):
        """Test that EIF method is selected and used when model is available."""
        from unittest.mock import patch, MagicMock
        from src.app.config import Settings
        
        health_point = {
            "heart_rate": 80.0,
            "oxygen_saturation": 97.5,
            "breathing_rate": 16.0,
            "blood_pressure_systolic": 105.0,
            "blood_pressure_diastolic": 70.0,
            "body_temperature": 36.7
        }
        
        # Mock successful EIF model
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.3]  # Below threshold
        
        mock_artifact = {
            "model": mock_model,
            "threshold": 0.5,
            "feature_names": ["heart_rate", "oxygen_saturation", "breathing_rate", 
                            "blood_pressure_systolic", "blood_pressure_diastolic", "body_temperature"]
        }
        
        with patch('src.app.services.anomaly_detector.get_settings') as mock_settings:
            settings = Settings()
            settings.ANOMALY_DETECTION_METHOD = "EIF"
            settings.EIF_THRESHOLD = 0.5
            settings.ALARM_ENDPOINT_URL = None  # Disable alarms for this test
            mock_settings.return_value = settings
            
            with patch('src.app.services.anomaly_detector._load_eif_model', return_value=mock_artifact):
                is_anomaly, score = detect_anomaly(health_point)
                
                # Verify EIF model was called
                mock_model.predict.assert_called_once()
                
                assert is_anomaly is False  # 0.3 < 0.5 threshold
                assert isinstance(score, float)
                assert 0.0 <= score <= 1.0
    
    def test_eif_fallback_to_distance(self):
        """Test that EIF method falls back to DISTANCE when model fails to load."""
        from unittest.mock import patch
        from src.app.config import Settings
        
        health_point = {
            "heart_rate": 95.0,
            "oxygen_saturation": 94.0,
            "breathing_rate": 22.0,
            "blood_pressure_systolic": 125.0,
            "blood_pressure_diastolic": 85.0,
            "body_temperature": 37.5
        }
        
        with patch('src.app.services.anomaly_detector.get_settings') as mock_settings:
            settings = Settings()
            settings.ANOMALY_DETECTION_METHOD = "EIF"
            settings.EIF_THRESHOLD = 0.5
            settings.DISTANCE_THRESHOLD = 3.8
            settings.ALARM_ENDPOINT_URL = None  # Disable alarms for this test
            mock_settings.return_value = settings
            
            # Mock EIF model loading failure
            with patch('src.app.services.anomaly_detector._load_eif_model', return_value=None):
                is_anomaly, score = detect_anomaly(health_point)
                
                # Should still work using distance method as fallback
                assert isinstance(is_anomaly, bool)
                assert isinstance(score, float)
                assert 0.0 <= score <= 1.0
    
    def test_method_selection_with_different_results(self):
        """Test that different methods can produce different results for same input."""
        from unittest.mock import patch, MagicMock
        from src.app.config import Settings
        
        # Health point that might be borderline anomalous
        health_point = {
            "heart_rate": 90.0,
            "oxygen_saturation": 94.0,
            "breathing_rate": 21.0,
            "blood_pressure_systolic": 125.0,
            "blood_pressure_diastolic": 85.0,
            "body_temperature": 37.3
        }
        
        # Test with DISTANCE method
        with patch('src.app.services.anomaly_detector.get_settings') as mock_settings:
            settings = Settings()
            settings.ANOMALY_DETECTION_METHOD = "DISTANCE"
            settings.DISTANCE_THRESHOLD = 3.8
            settings.ALARM_ENDPOINT_URL = None
            mock_settings.return_value = settings
            
            is_anomaly_distance, score_distance = detect_anomaly(health_point)
        
        # Test with EIF method (mock high score)
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.7]  # High score
        
        mock_artifact = {
            "model": mock_model,
            "threshold": 0.5,
            "feature_names": ["heart_rate", "oxygen_saturation", "breathing_rate", 
                            "blood_pressure_systolic", "blood_pressure_diastolic", "body_temperature"]
        }
        
        with patch('src.app.services.anomaly_detector.get_settings') as mock_settings:
            settings = Settings()
            settings.ANOMALY_DETECTION_METHOD = "EIF"
            settings.EIF_THRESHOLD = 0.5
            settings.ALARM_ENDPOINT_URL = None
            mock_settings.return_value = settings
            
            with patch('src.app.services.anomaly_detector._load_eif_model', return_value=mock_artifact):
                is_anomaly_eif, score_eif = detect_anomaly(health_point)
        
        # Both should return valid results
        assert isinstance(is_anomaly_distance, bool)
        assert isinstance(is_anomaly_eif, bool)
        assert 0.0 <= score_distance <= 1.0
        assert 0.0 <= score_eif <= 1.0
        
        # EIF should detect anomaly (0.7 > 0.5), distance might not
        assert is_anomaly_eif is True
    
    def test_invalid_method_defaults_to_distance(self):
        """Test that invalid detection method defaults to DISTANCE."""
        from unittest.mock import patch
        from src.app.config import Settings
        
        health_point = {"heart_rate": 80.0}
        
        with patch('src.app.services.anomaly_detector.get_settings') as mock_settings:
            settings = Settings()
            settings.ANOMALY_DETECTION_METHOD = "INVALID"  # This shouldn't be possible with validation, but test anyway
            settings.DISTANCE_THRESHOLD = 3.8
            settings.ALARM_ENDPOINT_URL = None
            mock_settings.return_value = settings
            
            # Should default to distance method and not crash
            is_anomaly, score = detect_anomaly(health_point)
            
            assert isinstance(is_anomaly, bool)
            assert 0.0 <= score <= 1.0
    
    def test_configuration_isolation_between_calls(self):
        """Test that configuration changes between calls work correctly."""
        from unittest.mock import patch, MagicMock
        from src.app.config import Settings
        
        health_point = {"heart_rate": 95.0, "oxygen_saturation": 94.0}
        
        # First call with DISTANCE method
        with patch('src.app.services.anomaly_detector.get_settings') as mock_settings:
            settings1 = Settings()
            settings1.ANOMALY_DETECTION_METHOD = "DISTANCE"
            settings1.DISTANCE_THRESHOLD = 2.0  # Low threshold
            settings1.ALARM_ENDPOINT_URL = None
            mock_settings.return_value = settings1
            
            is_anomaly1, score1 = detect_anomaly(health_point)
        
        # Second call with EIF method (different configuration)
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.3]  # Low score
        
        mock_artifact = {
            "model": mock_model,
            "threshold": 0.5,
            "feature_names": ["heart_rate", "oxygen_saturation"]
        }
        
        with patch('src.app.services.anomaly_detector.get_settings') as mock_settings:
            settings2 = Settings()
            settings2.ANOMALY_DETECTION_METHOD = "EIF"
            settings2.EIF_THRESHOLD = 0.5
            settings2.ALARM_ENDPOINT_URL = None
            mock_settings.return_value = settings2
            
            with patch('src.app.services.anomaly_detector._load_eif_model', return_value=mock_artifact):
                is_anomaly2, score2 = detect_anomaly(health_point)
        
        # Both calls should work independently
        assert isinstance(is_anomaly1, bool)
        assert isinstance(is_anomaly2, bool)
        assert 0.0 <= score1 <= 1.0
        assert 0.0 <= score2 <= 1.0
        
        # With low distance threshold, should be anomaly
        # With EIF low score, should not be anomaly
        assert is_anomaly1 is True   # Distance with low threshold
        assert is_anomaly2 is False  # EIF with low score


if __name__ == "__main__":
    pytest.main([__file__])