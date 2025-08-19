"""Data simulation services for health sensor data generation.

This module provides functionality to generate realistic health sensor data
with configurable parameters and automatic refresh capabilities.
"""

import numpy as np
import pandas as pd
import time
import json
import os
import tempfile
from typing import Dict, Optional

from src.app.config import get_settings
from src.app.constants import (
    HEALTH_PARAMS,
    SLIDER_TO_PARAM_MAPPING,
    DEFAULT_DISPERSION
)
from src.app.utils.math_utils import apply_variance_to_health_data

# Dataset generation constants
DEFAULT_DATASET_SIZE = 500
RANDOM_SEED = 42


def generate_dummy_data(dataset_size: int = DEFAULT_DATASET_SIZE) -> pd.DataFrame:
    """Generate dummy health data with normal values at rest.
    
    Args:
        dataset_size: Number of data points to generate
        
    Returns:
        DataFrame with simulated health parameters for normal resting state
    """
    parameter_names = list(HEALTH_PARAMS.keys())
    rng = np.random.default_rng(RANDOM_SEED)
    
    # Generate normal health data using resting parameters
    health_data = {
        param_name: rng.normal(
            HEALTH_PARAMS[param_name]["mean_rest"],
            HEALTH_PARAMS[param_name]["std_rest"], 
            dataset_size
        )
        for param_name in parameter_names
    }
    
    return pd.DataFrame(health_data)


def generate_health_point_with_variance(
    health_values: Dict[str, float], 
    variance_multiplier: float
) -> Dict[str, float]:
    """Generate health data point with applied variance.
    
    Args:
        health_values: Dictionary of health parameter values from UI sliders
        variance_multiplier: Multiplier for standard deviation (0.0 to 1.0)
        
    Returns:
        Dictionary of generated health parameter values with variance applied
    """
    # Convert slider values to parameter values using mapping
    parameter_values = {}
    variance_params = {}
    
    for slider_key, param_key in SLIDER_TO_PARAM_MAPPING.items():
        if slider_key in health_values:
            parameter_values[param_key] = health_values[slider_key]
            variance_params[param_key] = HEALTH_PARAMS[param_key]["std_rest"]
    
    return apply_variance_to_health_data(
        parameter_values, 
        variance_params, 
        variance_multiplier
    )


class HealthDataGenerator:
    """Manages automatic health data point generation with configurable intervals.
    
    This class handles the timing and generation of health data points for the
    Streamlit UI, ensuring data is refreshed at regular intervals while allowing
    immediate updates when UI parameters change. It also maintains the current
    state that can be accessed by API endpoints.
    """
    
    def __init__(self) -> None:
        """Initialize the health data generator with application settings."""
        self.settings = get_settings()
        self.last_generation_time: Optional[float] = None
        self.current_health_point: Optional[Dict[str, float]] = None
        self.current_health_values: Optional[Dict[str, float]] = None
        self.current_variance_multiplier: Optional[float] = None
    
    def generate_new_health_point(
        self, 
        health_values: Dict[str, float], 
        variance_multiplier: float
    ) -> Dict[str, float]:
        """Generate a new health point and update the generation timestamp.
        
        Args:
            health_values: Current health parameter values from UI
            variance_multiplier: Amount of variance to apply (0.0 to 1.0)
            
        Returns:
            Dictionary of generated health parameter values
        """
        current_time = time.time()
        self.last_generation_time = current_time
        self.current_health_values = health_values.copy()
        self.current_variance_multiplier = variance_multiplier
        self.current_health_point = generate_health_point_with_variance(
            health_values, variance_multiplier
        )
        return self.current_health_point
    
    def get_current_health_point(
        self, 
        health_values: Dict[str, float], 
        variance_multiplier: float
    ) -> Dict[str, float]:
        """Get current health point, always generating fresh data.
        
        This ensures that UI changes are immediately reflected in the visualization.
        Also updates the stored current state for API access.
        
        Args:
            health_values: Current health parameter values from UI
            variance_multiplier: Amount of variance to apply (0.0 to 1.0)
            
        Returns:
            Dictionary of generated health parameter values
        """
        # Update current state
        self.current_health_values = health_values.copy()
        self.current_variance_multiplier = variance_multiplier
        self.current_health_point = generate_health_point_with_variance(
            health_values, variance_multiplier
        )
        return self.current_health_point
    
    def get_last_health_point(self) -> Optional[Dict[str, float]]:
        """Get the last generated health point without generating a new one.
        
        This is used by the API endpoint to return the same values currently
        displayed in the Streamlit UI.
        
        Returns:
            Dictionary of last generated health parameter values, or None if no data
        """
        if self.current_health_point is None:
            # If no current point exists, generate one with default values
            default_values = get_default_health_values()
            self.current_health_values = default_values
            self.current_variance_multiplier = DEFAULT_DISPERSION
            self.current_health_point = generate_health_point_with_variance(
                default_values, DEFAULT_DISPERSION
            )
        return self.current_health_point


# Global shared instance for API endpoints
_shared_data_generator: Optional[HealthDataGenerator] = None

# Simple file-based storage for inter-process communication
_health_data_file = os.path.join(tempfile.gettempdir(), "health_sensor_vitals.json")
_last_health_point: Optional[Dict[str, float]] = None


def get_shared_data_generator() -> HealthDataGenerator:
    """Get the shared HealthDataGenerator instance for API endpoints.
    
    Returns:
        HealthDataGenerator: Shared instance for generating health data
    """
    global _shared_data_generator
    if _shared_data_generator is None:
        _shared_data_generator = HealthDataGenerator()
    return _shared_data_generator




def get_default_health_values() -> Dict[str, float]:
    """Get default health parameter values using mean rest values.
    
    Returns:
        Dict[str, float]: Default health parameter values mapped to slider keys
    """
    return {
        "heart_rate": HEALTH_PARAMS["heart_rate"]["mean_rest"],
        "oxygen_saturation": HEALTH_PARAMS["oxygen_saturation"]["mean_rest"],
        "breathing_rate": HEALTH_PARAMS["breathing_rate"]["mean_rest"],
        "systolic_bp": HEALTH_PARAMS["blood_pressure_systolic"]["mean_rest"],
        "diastolic_bp": HEALTH_PARAMS["blood_pressure_diastolic"]["mean_rest"],
        "body_temperature": HEALTH_PARAMS["body_temperature"]["mean_rest"]
    }


def store_current_health_point(health_point: Dict[str, float]) -> None:
    """Store the current health point in a file for inter-process communication.
    
    Args:
        health_point: Dictionary containing health parameter values
    """
    global _last_health_point
    _last_health_point = health_point.copy()
    
    try:
        # Write to temporary file, then atomic rename (prevents corruption)
        temp_file = _health_data_file + ".tmp"
        with open(temp_file, 'w') as f:
            json.dump(health_point, f)
        
        # Atomic rename (this is atomic on most filesystems)
        os.rename(temp_file, _health_data_file)
        # Successfully stored
        
    except Exception as e:
        print(f"[STORE] Error storing in file: {e}")
        # Data is still stored in _last_health_point as fallback

def get_stored_health_point() -> Dict[str, float]:
    """Get the stored health point from file for inter-process communication.
    
    Returns:
        Dictionary containing the last stored health parameter values
    """
    global _last_health_point
    
    try:
        # Try to read from file first
        if os.path.exists(_health_data_file):
            with open(_health_data_file, 'r') as f:
                health_point = json.load(f)
                _last_health_point = health_point
                # Successfully retrieved from file
                return health_point
        
    except Exception as e:
        print(f"[GET] Error reading file: {e}")
    
    # Fallback to last stored value in memory
    if _last_health_point is not None:
        # Using cached fallback
        return _last_health_point.copy()
    
    # No data found, generate defaults
    print("[GET] No data found, generating default values")
    default_values = get_default_health_values()
    default_point = generate_health_point_with_variance(default_values, DEFAULT_DISPERSION)
    store_current_health_point(default_point)
    return default_point
