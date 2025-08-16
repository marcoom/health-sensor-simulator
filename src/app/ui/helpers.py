"""Helper functions for the Streamlit health sensor simulator UI."""

import streamlit as st
from typing import Dict, Any, Union

from src.app.constants import HEALTH_PARAMS, DEFAULT_DISPERSION
from src.app.ui.config import SLIDER_CONFIG


def reset_to_rest_state() -> None:
    """Reset all slider values to their resting state defaults.
    
    This function iterates through all configured sliders and sets their
    session state values to the mean resting values from health parameters.
    """
    for config in SLIDER_CONFIG.values():
        param_key = config["param_key"] 
        session_key = config["session_key"]
        rest_value = HEALTH_PARAMS[param_key]["mean_rest"]
        st.session_state[session_key] = rest_value


def create_slider(container: Any, config: Dict[str, Union[str, type]]) -> Union[int, float]:
    """Create a Streamlit slider widget with the given configuration.
    
    Args:
        container: Streamlit container to place the slider in
        config: Slider configuration dictionary containing label, keys, and type
        
    Returns:
        Current value of the created slider
    """
    param_key = str(config["param_key"])
    session_key = str(config["session_key"])
    value_type = config["type"]
    label = str(config["label"])
    
    # Initialize session state with default value if not present
    if session_key not in st.session_state:
        default_value = HEALTH_PARAMS[param_key]["mean_rest"]
        st.session_state[session_key] = value_type(default_value)
    
    # Prepare slider arguments with proper typing
    slider_kwargs = {
        "min_value": value_type(HEALTH_PARAMS[param_key]["min_rest"]),
        "max_value": value_type(HEALTH_PARAMS[param_key]["max_rest"]),
        "key": session_key
    }
    
    # Add step parameter for float sliders for better precision
    if value_type == float:
        slider_kwargs["step"] = 0.1
        
    return container.slider(label, **slider_kwargs)



