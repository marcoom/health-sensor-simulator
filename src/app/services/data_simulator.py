"""Data simulation services for health sensor data generation.

This module provides functionality to generate realistic health sensor data
with configurable parameters and automatic refresh capabilities.
"""

import numpy as np
import pandas as pd
import time
from typing import Dict, Optional

from src.app.config import get_settings
from src.app.constants import (
    HEALTH_PARAMS,
    SLIDER_TO_PARAM_MAPPING,
    AUTO_REFRESH_CHECK_INTERVAL_SECONDS
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
    immediate updates when UI parameters change.
    """
    
    def __init__(self) -> None:
        """Initialize the health data generator with application settings."""
        self.settings = get_settings()
        self.last_generation_time: Optional[float] = None
        self.current_health_point: Optional[Dict[str, float]] = None
    
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
        
        Args:
            health_values: Current health parameter values from UI
            variance_multiplier: Amount of variance to apply (0.0 to 1.0)
            
        Returns:
            Dictionary of generated health parameter values
        """
        return generate_health_point_with_variance(health_values, variance_multiplier)
    
