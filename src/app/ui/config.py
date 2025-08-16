"""UI configuration for the Streamlit health sensor simulator."""

from typing import Dict, Any, Type, Union
from src.app.constants import DEFAULT_DISPERSION

# Slider configurations for the Streamlit UI
SLIDER_CONFIG: Dict[str, Dict[str, Union[str, Type]]] = {
    "heart_rate": {
        "label": "Heart Rate [bpm]",
        "param_key": "heart_rate",
        "session_key": "heart_rate",
        "type": int
    },
    "oxygen_saturation": {
        "label": "Oxygen Saturation [%]",
        "param_key": "oxygen_saturation", 
        "session_key": "oxygen_saturation",
        "type": int
    },
    "breathing_rate": {
        "label": "Breathing Rate [breaths/min]",
        "param_key": "breathing_rate",
        "session_key": "breathing_rate", 
        "type": int
    },
    "systolic_bp": {
        "label": "Systolic Blood Pressure [mmHg]",
        "param_key": "blood_pressure_systolic",
        "session_key": "systolic_bp",
        "type": int
    },
    "diastolic_bp": {
        "label": "Diastolic Blood Pressure [mmHg]",
        "param_key": "blood_pressure_diastolic",
        "session_key": "diastolic_bp",
        "type": int
    },
    "body_temperature": {
        "label": "Body Temperature [°C]",
        "param_key": "body_temperature",
        "session_key": "body_temperature",
        "type": float
    }
}

# Re-export DEFAULT_DISPERSION from constants
__all__ = ["SLIDER_CONFIG", "DEFAULT_DISPERSION"]