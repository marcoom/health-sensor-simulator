"""Anomaly detection service for health sensor data.

This module provides anomaly detection functionality for health sensor readings,
supporting both distance-based threshold approach and Extended Isolation Forest.
"""

from src.app.utils.logging import get_logger
import os
from datetime import datetime, timezone
from typing import Dict, Tuple, Optional, Any
import requests
import pandas as pd
from joblib import load
from src.app.utils.math_utils import calculate_radial_distance
from src.app.constants import create_health_center_point
from src.app.config import get_settings

logger = get_logger(__name__)

class _AnomalyDetectionCache:
    """Cache for loaded EIF model and settings to reduce global variables."""
    
    def __init__(self):
        self.eif_model: Optional[Dict[str, Any]] = None
        self.settings = None
    
    def get_eif_model(self) -> Optional[Dict[str, Any]]:
        """Get cached EIF model."""
        return self.eif_model
    
    def set_eif_model(self, model: Dict[str, Any]) -> None:
        """Set cached EIF model."""
        self.eif_model = model
    
    def get_settings(self):
        """Get cached settings to avoid repeated get_settings() calls."""
        if self.settings is None:
            self.settings = get_settings()
        return self.settings


# Single cache instance
_cache = _AnomalyDetectionCache()


def _load_eif_model() -> Optional[Dict[str, Any]]:
    """Load the Extended Isolation Forest model from disk with caching.
    
    Returns:
        Optional[Dict[str, Any]]: Model artifact containing model, threshold, and feature names,
                                 or None if loading fails
    """
    cached_model = _cache.get_eif_model()
    if cached_model is not None:
        return cached_model
    
        
    model_path = os.path.join(os.path.dirname(__file__), "..", "..", "models", "eif.joblib")
    model_path = os.path.abspath(model_path)
    
    try:
        if not os.path.exists(model_path):
            logger.error(f"EIF model file not found at {model_path}")
            return None
            
        artifact = load(model_path)
        logger.debug(f"Successfully loaded EIF model from {model_path}")
        
        # Validate artifact structure
        required_keys = ["model", "threshold", "feature_names"]
        if not all(key in artifact for key in required_keys):
            logger.error(f"Invalid EIF model artifact - missing keys: {required_keys}")
            return None
            
        _cache.set_eif_model(artifact)
        return artifact
        
    except Exception as e:
        logger.error(f"Failed to load EIF model: {e}")
        return None


def _detect_anomaly_eif(health_point: Dict[str, float]) -> Tuple[bool, float]:
    """Detect anomaly using Extended Isolation Forest method.
    
    Args:
        health_point: Dictionary containing health parameter values
        
    Returns:
        Tuple[bool, float]: (is_anomaly, anomaly_score)
            - is_anomaly: True if the point is anomalous (outlier), False otherwise
            - anomaly_score: Score between 0.0 and 1.0 representing anomaly certainty
    """
    artifact = _load_eif_model()
    if artifact is None:
        logger.warning("EIF model unavailable, falling back to distance method")
        return _detect_anomaly_distance(health_point)
    
    model = artifact["model"]
    threshold = artifact["threshold"]
    feature_names = artifact["feature_names"]
    
    try:
        # Create DataFrame with correct feature order
        X_new = pd.DataFrame([health_point], columns=feature_names)
        
        # Get anomaly score (higher = more anomalous in isotree)
        raw_score = float(model.predict(X_new)[0])
        
        # Use manual threshold from config instead of model threshold
        settings = _cache.get_settings()
        manual_threshold = settings.EIF_THRESHOLD
        
        # Determine if anomaly
        is_anomaly = raw_score >= manual_threshold
        
        # Convert to 0-1 anomaly certainty score
        # Raw EIF scores typically range around 0.2-0.8, with threshold around 0.5
        if raw_score <= 0.2:
            score = 0.0
        elif raw_score >= 0.8:
            score = 1.0
        else:
            # Linear scaling from 0.2-0.8 range to 0.0-1.0
            score = (raw_score - 0.2) / (0.8 - 0.2)
        
        return is_anomaly, score
        
    except Exception as e:
        logger.error(f"EIF prediction failed: {e}")
        logger.warning("Falling back to distance method")
        return _detect_anomaly_distance(health_point)


def _detect_anomaly_distance(health_point: Dict[str, float], threshold: Optional[float] = None) -> Tuple[bool, float]:
    """Detect anomaly using distance-based method.
    
    This function calculates the radial distance of a health data point from
    the center (mean resting values) and determines if it exceeds the threshold.
    It also returns a score between 0 and 1 representing anomaly certainty.
    
    Args:
        health_point: Dictionary containing health parameter values
        threshold: Distance threshold above which a point is considered anomalous.
                  If None, uses DISTANCE_THRESHOLD from config.
        
    Returns:
        Tuple[bool, float]: (is_anomaly, anomaly_score)
            - is_anomaly: True if the point is anomalous (outlier), False otherwise
            - anomaly_score: Score between 0.0 and 1.0 representing anomaly certainty
    """
    # Use config threshold if none provided
    if threshold is None:
        settings = _cache.get_settings()
        threshold = settings.DISTANCE_THRESHOLD
    # Create center point from mean resting values
    try:
        center_point = create_health_center_point(list(health_point.keys()))
    except KeyError:
        # Fallback: if any parameter not found, use the value itself as center
        center_point = dict(health_point)
    
    # Handle empty health point
    if not health_point:
        distance = 0.0
    else:
        # Calculate radial distance from center
        distance = calculate_radial_distance(health_point, center_point)
    
    # Determine if anomaly
    is_anomaly = distance > threshold
    
    # Calculate anomaly score (0.0 to 1.0)
    if distance <= threshold:
        # Normal range: score proportional to distance/threshold
        score = min(distance / threshold, 1.0) * 0.5  # Max 0.5 for normal values
    elif threshold < distance <= 4.0:
        # Mild anomaly range: score between 0.5 and 0.75
        score = 0.5 + ((distance - threshold) / (4.0 - threshold)) * 0.25
    else:
        # Severe anomaly range: score between 0.75 and 1.0
        max_distance = 6.0  # Define a max distance for scoring
        score = 0.75 + min((distance - 4.0) / (max_distance - 4.0), 1.0) * 0.25
        score = min(score, 1.0)  # Cap at 1.0
    
    return is_anomaly, score


def _send_anomaly_alarm(health_point: Dict[str, float], anomaly_score: float) -> bool:
    """Send anomaly alarm to configured endpoint.
    
    Args:
        health_point: Dictionary containing health parameter values
        anomaly_score: The anomaly certainty score (0.0-1.0)
        
    Returns:
        bool: True if alarm was sent successfully, False otherwise
    """
    settings = _cache.get_settings()
    
    if not settings.ALARM_ENDPOINT_URL:
        logger.debug("No ALARM_ENDPOINT_URL configured, skipping alarm notification")
        return False
        
    
    # Prepare payload matching AnomalyResponse schema
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "anomaly_score": anomaly_score,
        "vitals": health_point
    }
    
    try:
        response = requests.post(
            settings.ALARM_ENDPOINT_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10.0
        )
        
        if response.status_code in (200, 201, 202):
            logger.debug(f"Anomaly alarm sent successfully to {settings.ALARM_ENDPOINT_URL}")
            return True
        else:
            logger.debug(
                f"Alarm endpoint responded with status {response.status_code}: {response.text}"
            )
            return False
            
    except requests.exceptions.ConnectionError:
        logger.debug(f"No alarm server listening at {settings.ALARM_ENDPOINT_URL}")
        return False
    except requests.exceptions.Timeout:
        logger.debug(f"Timeout sending alarm to {settings.ALARM_ENDPOINT_URL}")
        return False
    except Exception as e:
        logger.error(f"Failed to send anomaly alarm to {settings.ALARM_ENDPOINT_URL}: {e}")
        return False


def detect_anomaly(health_point: Dict[str, float]) -> Tuple[bool, float]:
    """Detect if a health data point is anomalous and calculate anomaly score.
    
    This function uses the configured anomaly detection method (DISTANCE or EIF)
    to determine if a health data point is anomalous and calculate a certainty score.
    
    Args:
        health_point: Dictionary containing health parameter values
        
    Returns:
        Tuple[bool, float]: (is_anomaly, anomaly_score)
            - is_anomaly: True if the point is anomalous (outlier), False otherwise
            - anomaly_score: Score between 0.0 and 1.0 representing anomaly certainty
    """
    settings = _cache.get_settings()
    
    # Choose detection method based on configuration
    if settings.ANOMALY_DETECTION_METHOD == "EIF":
        is_anomaly, score = _detect_anomaly_eif(health_point)
        method_name = "EIF"
    else:  # Default to DISTANCE method
        is_anomaly, score = _detect_anomaly_distance(health_point)
        method_name = "DISTANCE"
    
    # Log anomaly detection at DEBUG level and send alarm if needed
    if is_anomaly:
        logger.debug(
            f"Anomaly detected using {method_name} method - Score: {score:.3f}, "
            f"Health values: {health_point}"
        )
        
        # Send alarm notification
        _send_anomaly_alarm(health_point, score)
    
    return is_anomaly, score


