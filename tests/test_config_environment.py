"""Tests for configuration and environment variable handling."""

import os
import tempfile
from unittest.mock import patch, mock_open
import pytest

from src.app.config import Settings, get_settings


class TestEnvironmentVariableOverrides:
    """Test that environment variables properly override configuration defaults."""
    
    def test_log_level_environment_override(self):
        """Test that LOG_LEVEL environment variable overrides default."""
        # Test each valid log level
        for env_level in ["DEBUG", "INFO", "WARNING"]:
            with patch.dict(os.environ, {"LOG_LEVEL": env_level}, clear=True):
                settings = Settings()
                assert settings.LOG_LEVEL == env_level
    
    def test_anomaly_detection_method_environment_override(self):
        """Test that ANOMALY_DETECTION_METHOD environment variable overrides default."""
        # Test both valid detection methods
        for method in ["DISTANCE", "EIF"]:
            with patch.dict(os.environ, {"ANOMALY_DETECTION_METHOD": method}, clear=True):
                settings = Settings()
                assert settings.ANOMALY_DETECTION_METHOD == method
    
    def test_eif_threshold_environment_override(self):
        """Test that EIF_THRESHOLD environment variable overrides default."""
        test_values = ["0.3", "0.5", "0.7"]
        for threshold_str in test_values:
            with patch.dict(os.environ, {"EIF_THRESHOLD": threshold_str}, clear=True):
                settings = Settings()
                assert settings.EIF_THRESHOLD == float(threshold_str)
    
    def test_distance_threshold_environment_override(self):
        """Test that DISTANCE_THRESHOLD environment variable overrides default."""
        test_values = ["2.0", "3.8", "5.0"]
        for threshold_str in test_values:
            with patch.dict(os.environ, {"DISTANCE_THRESHOLD": threshold_str}, clear=True):
                settings = Settings()
                assert settings.DISTANCE_THRESHOLD == float(threshold_str)
    
    def test_alarm_endpoint_url_environment_override(self):
        """Test that ALARM_ENDPOINT_URL environment variable overrides default."""
        test_urls = [
            "http://localhost:8080/alerts",
            "https://api.example.com/webhooks/alerts",
            "http://192.168.1.100:9000/notify"
        ]
        for url in test_urls:
            with patch.dict(os.environ, {"ALARM_ENDPOINT_URL": url}, clear=True):
                settings = Settings()
                assert settings.ALARM_ENDPOINT_URL == url
    
    def test_multiple_environment_overrides(self):
        """Test that multiple environment variables work together."""
        env_vars = {
            "LOG_LEVEL": "DEBUG",
            "ANOMALY_DETECTION_METHOD": "EIF",
            "EIF_THRESHOLD": "0.6",
            "DISTANCE_THRESHOLD": "4.0",
            "ALARM_ENDPOINT_URL": "http://test.example.com/alerts"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.LOG_LEVEL == "DEBUG"
            assert settings.ANOMALY_DETECTION_METHOD == "EIF"
            assert settings.EIF_THRESHOLD == 0.6
            assert settings.DISTANCE_THRESHOLD == 4.0
            assert settings.ALARM_ENDPOINT_URL == "http://test.example.com/alerts"
    
    def test_partial_environment_overrides(self):
        """Test that only specified environment variables are overridden."""
        # Only set LOG_LEVEL, others should use defaults
        with patch.dict(os.environ, {"LOG_LEVEL": "WARNING"}, clear=True):
            # Disable .env file loading for this test
            with patch('src.app.config.Settings.Config.env_file', None):
                settings = Settings()
                assert settings.LOG_LEVEL == "WARNING"  # Overridden
                assert settings.ANOMALY_DETECTION_METHOD == "DISTANCE"  # Default
                assert settings.EIF_THRESHOLD == 0.4  # Default
                assert settings.DISTANCE_THRESHOLD == 3.8  # Default
    
    def test_invalid_environment_values(self):
        """Test that invalid environment values raise validation errors."""
        from pydantic import ValidationError
        
        # Invalid LOG_LEVEL
        with patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}, clear=True):
            with pytest.raises(ValidationError):
                Settings()
        
        # Invalid ANOMALY_DETECTION_METHOD
        with patch.dict(os.environ, {"ANOMALY_DETECTION_METHOD": "INVALID"}, clear=True):
            with pytest.raises(ValidationError):
                Settings()
        
        # Invalid numeric values
        with patch.dict(os.environ, {"EIF_THRESHOLD": "not_a_number"}, clear=True):
            with pytest.raises(ValidationError):
                Settings()



class TestConfigurationIntegration:
    """Test configuration integration with other components."""
    
    def test_get_settings_function_environment_isolation(self):
        """Test that get_settings function works with environment isolation."""
        # Test with clean environment
        with patch.dict(os.environ, {}, clear=True):
            settings = get_settings()
            assert settings.LOG_LEVEL == "INFO"  # Default
        
        # Test with environment override
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}, clear=True):
            settings = get_settings()
            assert settings.LOG_LEVEL == "DEBUG"  # Overridden
    
    def test_logging_config_with_environment_override(self):
        """Test that logging configuration uses environment-overridden values."""
        with patch.dict(os.environ, {"LOG_LEVEL": "WARNING"}, clear=True):
            settings = Settings()
            logging_config = settings.get_logging_config()
            
            # Both handler and logger should use the overridden level
            assert logging_config["handlers"]["consoleHandler"]["level"] == "WARNING"
            assert logging_config["loggers"]["src"]["level"] == "WARNING"
    
    def test_configuration_defaults_isolation(self):
        """Test that configuration defaults are not affected by previous tests."""
        # This test ensures test isolation is working properly
        with patch.dict(os.environ, {}, clear=True):
            # Disable .env file loading to test true defaults
            with patch('src.app.config.Settings.Config.env_file', None):
                settings = Settings()
                
                # Verify all defaults
                assert settings.PROJECT_NAME == "Health Sensor Simulator"
                assert settings.PROJECT_SLUG == "health_sensor_simulator"
                assert settings.DEBUG is True
                assert settings.API_STR == "/api/v1"
                assert settings.LOG_LEVEL == "INFO"
                assert settings.DATA_GENERATION_INTERVAL_SECONDS == 5
                assert settings.FASTAPI_HOST == "0.0.0.0"
                assert settings.FASTAPI_PORT == 8000
                assert settings.STREAMLIT_HOST == "0.0.0.0"
                assert settings.STREAMLIT_PORT == 8501
                assert settings.ANOMALY_DETECTION_METHOD == "DISTANCE"
                assert settings.EIF_THRESHOLD == 0.4
                assert settings.DISTANCE_THRESHOLD == 3.8
                assert settings.ALARM_ENDPOINT_URL is None


class TestConfigurationEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_environment_variable(self):
        """Test behavior with empty environment variables."""
        with patch.dict(os.environ, {"ALARM_ENDPOINT_URL": ""}, clear=True):
            settings = Settings()
            # Empty string should be preserved, not converted to None
            assert settings.ALARM_ENDPOINT_URL == ""
    
    def test_whitespace_environment_variable(self):
        """Test behavior with whitespace-only environment variables."""
        with patch.dict(os.environ, {"ALARM_ENDPOINT_URL": "  "}, clear=True):
            settings = Settings()
            # Whitespace should be preserved
            assert settings.ALARM_ENDPOINT_URL == "  "
    
    def test_case_sensitive_environment_variables(self):
        """Test that environment variables are case-sensitive."""
        # lowercase should not work (pydantic is case-sensitive by default)
        with patch.dict(os.environ, {"log_level": "DEBUG"}, clear=True):
            settings = Settings()
            # Should use default, not the lowercase version
            assert settings.LOG_LEVEL == "INFO"
        
        # Uppercase should work
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}, clear=True):
            settings = Settings()
            assert settings.LOG_LEVEL == "DEBUG"