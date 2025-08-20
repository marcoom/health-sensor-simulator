"""Helper functions for the Streamlit health sensor simulator UI."""

import streamlit as st
from typing import Dict, Any, Union

from src.app.constants import get_health_param_mean, get_health_param_range




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
        default_value = get_health_param_mean(param_key)
        st.session_state[session_key] = value_type(default_value)
    
    # Prepare slider arguments with proper typing
    min_val, max_val = get_health_param_range(param_key)
    slider_kwargs = {
        "min_value": value_type(min_val),
        "max_value": value_type(max_val),
        "key": session_key
    }
    
    # Add step parameter for float sliders for better precision
    if value_type == float:
        slider_kwargs["step"] = 0.1
        
    return container.slider(label, **slider_kwargs)



