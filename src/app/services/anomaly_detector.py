"""Anomaly detection service for health sensor data.

This module provides anomaly detection functionality for health sensor readings,
currently implementing a simple distance-based threshold approach that will be
replaced with Extended Isolation Forest in the future.
"""

from typing import Dict, Tuple
from src.app.utils.math_utils import calculate_radial_distance
from src.app.constants import HEALTH_PARAMS


def detect_anomaly(health_point: Dict[str, float], threshold: float = 3.8) -> Tuple[bool, float]:
    """Detect if a health data point is anomalous and calculate anomaly score.
    
    This function calculates the radial distance of a health data point from
    the center (mean resting values) and determines if it exceeds the threshold.
    It also returns a score between 0 and 1 representing anomaly certainty.
    
    Args:
        health_point: Dictionary containing health parameter values
        threshold: Distance threshold above which a point is considered anomalous
        
    Returns:
        Tuple[bool, float]: (is_anomaly, anomaly_score)
            - is_anomaly: True if the point is anomalous (outlier), False otherwise
            - anomaly_score: Score between 0.0 and 1.0 representing anomaly certainty
    """
    # Create center point from mean resting values
    center_point = {}
    for param_name in health_point.keys():
        if param_name in HEALTH_PARAMS:
            center_point[param_name] = HEALTH_PARAMS[param_name]["mean_rest"]
        else:
            # If parameter not in HEALTH_PARAMS, use the value itself as center
            center_point[param_name] = health_point[param_name]
    
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


