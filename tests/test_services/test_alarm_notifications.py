"""Tests for anomaly alarm notifications."""

import json
import logging
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest.mock import patch, MagicMock
import pytest
import requests

from src.app.services.anomaly_detector import _send_anomaly_alarm, detect_anomaly
from src.app.config import Settings


class AlarmHandler(BaseHTTPRequestHandler):
    """Test HTTP handler to capture POST requests."""
    
    received_requests = []
    
    def do_POST(self):
        """Handle POST requests and store them for verification."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        # Store the request for later verification
        request_data = {
            'path': self.path,
            'headers': dict(self.headers),
            'body': post_data.decode('utf-8'),
            'json': json.loads(post_data.decode('utf-8')) if post_data else None
        }
        AlarmHandler.received_requests.append(request_data)
        
        # Send successful response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "received"}')
    
    def log_message(self, format, *args):
        """Suppress log messages during tests."""
        pass
    
    @classmethod
    def clear_requests(cls):
        """Clear stored requests."""
        cls.received_requests = []


class AlarmServer:
    """Context manager for test HTTP server."""
    
    def __init__(self, port=8081):
        self.port = port
        self.server = None
        self.thread = None
    
    def __enter__(self):
        """Start the test server."""
        AlarmHandler.clear_requests()
        self.server = HTTPServer(('localhost', self.port), AlarmHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        time.sleep(0.1)  # Give server time to start
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the test server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.thread:
            self.thread.join(timeout=1)
    
    @property
    def received_requests(self):
        """Get all received requests."""
        return AlarmHandler.received_requests


class TestAlarmNotifications:
    """Test alarm notification functionality."""
    
    def test_send_alarm_success(self):
        """Test successful alarm sending."""
        health_point = {
            "heart_rate": 95.5,
            "oxygen_saturation": 88.2,
            "breathing_rate": 22.1,
            "blood_pressure_systolic": 140.3,
            "blood_pressure_diastolic": 85.7,
            "body_temperature": 37.8
        }
        anomaly_score = 0.85
        
        with AlarmServer() as server:
            with patch('src.app.services.anomaly_detector._cache.get_settings') as mock_settings:
                # Configure mock settings
                settings = Settings()
                settings.ALARM_ENDPOINT_URL = f"http://localhost:{server.port}/alerts"
                mock_settings.return_value = settings
                
                # Send alarm
                result = _send_anomaly_alarm(health_point, anomaly_score)
                
                # Verify success
                assert result is True
                assert len(server.received_requests) == 1
                
                # Verify request details
                request = server.received_requests[0]
                assert request['path'] == '/alerts'
                assert request['headers']['Content-Type'] == 'application/json'
                
                # Verify payload structure
                payload = request['json']
                assert 'ts' in payload
                assert payload['anomaly_score'] == anomaly_score
                assert payload['vitals'] == health_point
                
                # Verify timestamp format (ISO format)
                assert 'T' in payload['ts']
                assert payload['ts'].endswith('Z') or '+' in payload['ts']
    
    def test_send_alarm_connection_error(self, caplog_debug):
        """Test alarm sending with connection error."""
        health_point = {"heart_rate": 95.5}
        anomaly_score = 0.75
        
        # Set logger for the specific module
        caplog_debug.set_level(logging.DEBUG, logger="src.app.services.anomaly_detector")
        
        with patch('src.app.services.anomaly_detector._cache.get_settings') as mock_settings:
            # Configure mock settings with non-existent endpoint
            settings = Settings()
            settings.ALARM_ENDPOINT_URL = "http://localhost:9999/alerts"
            mock_settings.return_value = settings
            
            # Send alarm (should fail)
            result = _send_anomaly_alarm(health_point, anomaly_score)
            
            # Verify failure and debug log
            assert result is False
            assert "No alarm server listening at" in caplog_debug.text
    
    def test_send_alarm_timeout(self, caplog_debug):
        """Test alarm sending with timeout."""
        health_point = {"heart_rate": 95.5}
        anomaly_score = 0.75
        
        # Set logger for the specific module
        caplog_debug.set_level(logging.DEBUG, logger="src.app.services.anomaly_detector")
        
        with patch('src.app.services.anomaly_detector._cache.get_settings') as mock_settings:
            with patch('src.app.services.anomaly_detector.requests.post') as mock_post:
                # Configure mock settings
                settings = Settings()
                settings.ALARM_ENDPOINT_URL = "http://localhost:8080/alerts"
                mock_settings.return_value = settings
                
                # Mock timeout exception
                mock_post.side_effect = requests.exceptions.Timeout()
                
                # Send alarm (should fail)
                result = _send_anomaly_alarm(health_point, anomaly_score)
                
                # Verify failure and debug log
                assert result is False
                assert "Timeout sending alarm to" in caplog_debug.text
    
    def test_send_alarm_no_url_configured(self, caplog_debug):
        """Test alarm sending with no URL configured."""
        health_point = {"heart_rate": 95.5}
        anomaly_score = 0.75
        
        # Set logger for the specific module
        caplog_debug.set_level(logging.DEBUG, logger="src.app.services.anomaly_detector")
        
        with patch('src.app.services.anomaly_detector._cache.get_settings') as mock_settings:
            # Configure mock settings with no alarm URL
            settings = Settings()
            settings.ALARM_ENDPOINT_URL = None
            mock_settings.return_value = settings
            
            # Send alarm (should skip)
            result = _send_anomaly_alarm(health_point, anomaly_score)
            
            # Verify skip and debug log
            assert result is False
            assert "No ALARM_ENDPOINT_URL configured" in caplog_debug.text
    
    def test_send_alarm_http_error_status(self):
        """Test alarm sending with HTTP error response."""
        health_point = {"heart_rate": 95.5}
        anomaly_score = 0.75
        
        # Create a server that returns 500 error
        class ErrorHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'Internal Server Error')
            
            def log_message(self, format, *args):
                pass
        
        with patch('src.app.services.anomaly_detector._cache.get_settings') as mock_settings:
            settings = Settings()
            settings.ALARM_ENDPOINT_URL = "http://localhost:8082/alerts"
            mock_settings.return_value = settings
            
            # Start error server
            server = HTTPServer(('localhost', 8082), ErrorHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            time.sleep(0.1)
            
            try:
                # Send alarm (should fail)
                result = _send_anomaly_alarm(health_point, anomaly_score)
                assert result is False
            finally:
                server.shutdown()
                server.server_close()
    
    def test_detect_anomaly_with_alarm_integration(self):
        """Test full anomaly detection with alarm integration."""
        # Health point that should trigger anomaly (extreme values)
        health_point = {
            "heart_rate": 150.0,  # Very high
            "oxygen_saturation": 85.0,  # Very low
            "breathing_rate": 25.0,  # High
            "blood_pressure_systolic": 180.0,  # Very high
            "blood_pressure_diastolic": 95.0,  # High
            "body_temperature": 39.5  # Very high fever
        }
        
        with AlarmServer() as server:
            with patch('src.app.services.anomaly_detector._cache.get_settings') as mock_settings:
                # Configure mock settings
                settings = Settings()
                settings.ALARM_ENDPOINT_URL = f"http://localhost:{server.port}/alerts"
                settings.ANOMALY_DETECTION_METHOD = "DISTANCE"
                settings.DISTANCE_THRESHOLD = 3.0  # Lower threshold for easier triggering
                mock_settings.return_value = settings
                
                # Run anomaly detection
                is_anomaly, score = detect_anomaly(health_point)
                
                # Verify anomaly was detected
                assert is_anomaly is True
                assert score > 0.5  # Should be high score for extreme values
                
                # Verify alarm was sent
                assert len(server.received_requests) == 1
                request = server.received_requests[0]
                payload = request['json']
                
                assert payload['anomaly_score'] == score
                assert payload['vitals'] == health_point
    
    def test_detect_anomaly_no_alarm_for_normal_values(self):
        """Test that normal values don't trigger alarms."""
        # Normal health values (close to mean resting values)
        health_point = {
            "heart_rate": 80.0,      # mean_rest = 80.0
            "oxygen_saturation": 97.5, # mean_rest = 97.5
            "breathing_rate": 16.0,   # mean_rest = 16.0
            "blood_pressure_systolic": 105.0,  # mean_rest = 105.0
            "blood_pressure_diastolic": 70.0,  # mean_rest = 70.0
            "body_temperature": 36.7  # mean_rest = 36.7
        }
        
        with AlarmServer() as server:
            with patch('src.app.services.anomaly_detector._cache.get_settings') as mock_settings:
                # Configure mock settings
                settings = Settings()
                settings.ALARM_ENDPOINT_URL = f"http://localhost:{server.port}/alerts"
                settings.ANOMALY_DETECTION_METHOD = "DISTANCE"
                settings.DISTANCE_THRESHOLD = 3.8
                mock_settings.return_value = settings
                
                # Run anomaly detection
                is_anomaly, score = detect_anomaly(health_point)
                
                # Verify no anomaly was detected
                assert is_anomaly is False
                assert score < 0.5  # Should be low score for normal values
                
                # Verify no alarm was sent
                assert len(server.received_requests) == 0


@pytest.fixture
def caplog_debug(caplog):
    """Set logging level to DEBUG for tests."""
    import logging
    caplog.set_level(logging.DEBUG)
    return caplog