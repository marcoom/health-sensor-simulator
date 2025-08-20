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
    DEFAULT_DISPERSION,
    get_health_param_mean,
    get_health_param_std
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
            variance_params[param_key] = get_health_param_std(param_key)
    
    return apply_variance_to_health_data(
        parameter_values, 
        variance_params, 
        variance_multiplier
    )



# Simple file-based storage for inter-process communication
_HEALTH_DATA_FILE = os.path.join(tempfile.gettempdir(), "health_sensor_vitals.json")
_last_health_point: Optional[Dict[str, float]] = None






def get_health_data_file_path() -> str:
    """Get the path to the health data file for testing purposes.
    
    Returns:
        str: Path to the health data file
    """
    return _HEALTH_DATA_FILE


def get_default_health_values() -> Dict[str, float]:
    """Get default health parameter values using mean rest values.
    
    Returns:
        Dict[str, float]: Default health parameter values mapped to slider keys
    """
    return {
        "heart_rate": get_health_param_mean("heart_rate"),
        "oxygen_saturation": get_health_param_mean("oxygen_saturation"),
        "breathing_rate": get_health_param_mean("breathing_rate"),
        "systolic_bp": get_health_param_mean("blood_pressure_systolic"),
        "diastolic_bp": get_health_param_mean("blood_pressure_diastolic"),
        "body_temperature": get_health_param_mean("body_temperature")
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
        temp_file = _HEALTH_DATA_FILE + ".tmp"
        with open(temp_file, 'w') as f:
            json.dump(health_point, f)
        
        # Atomic rename (this is atomic on most filesystems)
        os.rename(temp_file, _HEALTH_DATA_FILE)
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
        if os.path.exists(_HEALTH_DATA_FILE):
            with open(_HEALTH_DATA_FILE, 'r') as f:
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
