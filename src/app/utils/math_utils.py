"""Mathematical utility functions for health sensor calculations."""

import numpy as np
from typing import Dict, List, Tuple, Any
from sklearn.preprocessing import StandardScaler


def calculate_radial_distance(data_point: Dict[str, float], center_point: Dict[str, float]) -> float:
    """Calculate the radial distance from a center point using standardized coordinates.
    
    This function computes the distance in a 6-dimensional health parameter space,
    applying standardization to ensure all parameters contribute equally despite
    different scales and units.
    
    Args:
        data_point: Dictionary of health parameter values
        center_point: Dictionary of center/reference values
        
    Returns:
        float: Standardized radial distance from center point
    """
    # Extract features in consistent order
    feature_names = sorted(data_point.keys())
    
    # Create arrays for calculation
    point_array = np.array([data_point[name] for name in feature_names]).reshape(1, -1)
    center_array = np.array([center_point[name] for name in feature_names]).reshape(1, -1)
    
    # Standardize both points using the center as reference
    scaler = StandardScaler()
    scaler.fit(center_array)
    
    point_scaled = scaler.transform(point_array)
    center_scaled = scaler.transform(center_array)
    
    # Calculate Euclidean distance in standardized space
    distance = np.linalg.norm(point_scaled - center_scaled)
    
    return float(distance)


def apply_variance_to_health_data(
    base_values: Dict[str, float], 
    variance_params: Dict[str, float], 
    variance_multiplier: float
) -> Dict[str, float]:
    """Apply variance to health data values using normal distribution.
    
    Args:
        base_values: Base health parameter values
        variance_params: Standard deviation for each parameter
        variance_multiplier: Multiplier for variance (0.0 to 1.0)
        
    Returns:
        Dictionary of health values with applied variance
    """
    result = {}
    rng = np.random.default_rng()
    
    for param_name, base_value in base_values.items():
        if param_name in variance_params:
            std_dev = variance_params[param_name] * variance_multiplier
            
            if std_dev > 0:
                generated_value = rng.normal(base_value, std_dev)
            else:
                generated_value = base_value
                
            result[param_name] = generated_value
        else:
            result[param_name] = base_value
    
    return result


def create_artificial_center_points(num_points: int = 50) -> List[Tuple[float, float]]:
    """Create artificial center points for visualization density.
    
    This addresses the "curse of dimensionality" in 6D space where normal
    distributions naturally form ring patterns rather than clusters.
    
    Args:
        num_points: Number of artificial center points to create
        
    Returns:
        List of (theta, distance) tuples for polar coordinates
    """
    rng = np.random.default_rng(42)  # Fixed seed for consistency
    
    # Create points clustered near the center
    center_points = []
    for _ in range(num_points):
        # Small random angles and very small distances for center cluster
        theta = rng.uniform(0, 2 * np.pi)
        # Most points very close to center, with exponential falloff
        distance = rng.exponential(0.1)  # Small scale for tight clustering
        center_points.append((theta, distance))
    
    return center_points


def validate_health_parameter_ranges(
    health_data: Dict[str, float], 
    parameter_specs: Dict[str, Dict[str, Any]]
) -> Dict[str, bool]:
    """Validate health parameters against their normal ranges.
    
    Args:
        health_data: Health parameter values to validate
        parameter_specs: Parameter specifications with min/max ranges
        
    Returns:
        Dictionary mapping parameter names to validation status
    """
    validation_results = {}
    
    for param_name, value in health_data.items():
        if param_name in parameter_specs:
            spec = parameter_specs[param_name]
            min_val = spec.get('min_rest', float('-inf'))
            max_val = spec.get('max_rest', float('inf'))
            
            validation_results[param_name] = min_val <= value <= max_val
        else:
            # Unknown parameter, mark as invalid
            validation_results[param_name] = False
    
    return validation_results