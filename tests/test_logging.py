"""Tests for logging configuration and LOG_LEVEL functionality."""
import logging
import os
from unittest.mock import patch
import pytest

from health_sensor_simulator.app.config import Settings, get_settings


class TestLoggingConfiguration:
    """Test logging configuration with different log levels."""

    def test_default_log_level_is_info(self):
        """Test that default LOG_LEVEL is INFO."""
        settings = Settings()
        assert settings.LOG_LEVEL == "INFO"

    def test_log_level_can_be_set_to_debug(self):
        """Test that LOG_LEVEL can be set to DEBUG."""
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
            settings = Settings()
            assert settings.LOG_LEVEL == "DEBUG"

    def test_log_level_can_be_set_to_warning(self):
        """Test that LOG_LEVEL can be set to WARNING."""
        with patch.dict(os.environ, {"LOG_LEVEL": "WARNING"}):
            settings = Settings()
            assert settings.LOG_LEVEL == "WARNING"

    def test_log_level_can_be_set_to_info(self):
        """Test that LOG_LEVEL can be set to INFO."""
        with patch.dict(os.environ, {"LOG_LEVEL": "INFO"}):
            settings = Settings()
            assert settings.LOG_LEVEL == "INFO"

    def test_logging_config_uses_log_level(self):
        """Test that logging configuration uses the LOG_LEVEL setting."""
        settings = Settings(LOG_LEVEL="WARNING")
        logging_config = settings.get_logging_config()
        
        # Check handler level
        assert logging_config["handlers"]["consoleHandler"]["level"] == "WARNING"
        # Check logger level
        assert logging_config["loggers"]["health_sensor_simulator"]["level"] == "WARNING"

    def test_logging_config_structure(self):
        """Test that logging configuration has correct structure."""
        settings = Settings()
        logging_config = settings.get_logging_config()
        
        # Check required keys
        assert "version" in logging_config
        assert "disable_existing_loggers" in logging_config
        assert "formatters" in logging_config
        assert "handlers" in logging_config
        assert "loggers" in logging_config
        
        # Check formatters
        assert "standardFormatter" in logging_config["formatters"]
        
        # Check handlers
        assert "consoleHandler" in logging_config["handlers"]
        handler = logging_config["handlers"]["consoleHandler"]
        assert handler["class"] == "logging.StreamHandler"
        assert handler["formatter"] == "standardFormatter"
        
        # Check loggers
        assert "health_sensor_simulator" in logging_config["loggers"]
        assert "uvicorn" in logging_config["loggers"]
        assert "uvicorn.access" in logging_config["loggers"]

    def test_get_settings_returns_settings_instance(self):
        """Test that get_settings returns a Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)
        assert hasattr(settings, "LOG_LEVEL")

    def test_invalid_log_level_not_allowed(self):
        """Test that invalid log levels are not allowed by pydantic validation."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError, match="unexpected value; permitted: 'DEBUG', 'INFO', 'WARNING'"):
            Settings(LOG_LEVEL="INVALID")

    def test_logging_config_with_different_levels(self):
        """Test logging configuration with all valid log levels."""
        for level in ["DEBUG", "INFO", "WARNING"]:
            settings = Settings(LOG_LEVEL=level)
            logging_config = settings.get_logging_config()
            
            assert logging_config["handlers"]["consoleHandler"]["level"] == level
            assert logging_config["loggers"]["health_sensor_simulator"]["level"] == level


class TestStartupLogging:
    """Test startup logging functionality."""

    def test_startup_log_message_format(self):
        """Test that startup message has correct format."""
        import logging
        from io import StringIO
        import sys
        
        # Capture log output
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger("health_sensor_simulator")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Test the log message directly
        from health_sensor_simulator.app.config import get_settings
        settings = get_settings()
        logger.info(f"Starting {settings.PROJECT_NAME} with log level: {settings.LOG_LEVEL}")
        
        # Check the output
        log_output = log_capture.getvalue()
        assert "Starting Health Sensor Simulator" in log_output
        assert "log level:" in log_output
        assert settings.LOG_LEVEL in log_output
        
        # Clean up
        logger.removeHandler(handler)

    def test_startup_message_with_different_log_levels(self):
        """Test that startup message contains the correct log level."""
        import logging
        from io import StringIO
        
        for level in ["DEBUG", "INFO", "WARNING"]:
            with patch.dict(os.environ, {"LOG_LEVEL": level}):
                # Capture log output
                log_capture = StringIO()
                handler = logging.StreamHandler(log_capture)
                logger = logging.getLogger("health_sensor_simulator")
                logger.addHandler(handler)
                logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels
                
                # Test the log message
                from health_sensor_simulator.app.config import Settings
                settings = Settings()
                logger.info(f"Starting {settings.PROJECT_NAME} with log level: {settings.LOG_LEVEL}")
                
                # Check the output
                log_output = log_capture.getvalue()
                assert f"log level: {level}" in log_output
                
                # Clean up
                logger.removeHandler(handler)