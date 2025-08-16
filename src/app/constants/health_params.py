"""Health parameter constants and specifications.

This module contains all health-related constants including parameter ranges,
default values, and timing configurations for the health sensor simulator.
"""

from typing import Dict, Any

# Health parameters for different physiological states
HEALTH_PARAMS: Dict[str, Dict[str, Any]] = {
    "heart_rate": {
        "mean_rest": 80.0,     # average at rest (bpm)
        "std_rest": 6.7,       # variability at rest
        "min_rest": 60.0,      # lower normal resting rate
        "max_rest": 100.0,     # upper normal resting rate
        "abs_min": 0.0,        # cardiac arrest, death
        "abs_max": 300.0,      # beyond refractory limit, cardiac arrest
        "mean_activity": 120.0, # average during moderate exercise
        "mean_sleep": 60.0     # average during sleep
    },
    "oxygen_saturation": {
        "mean_rest": 97.5,     # average at rest (%)
        "std_rest": 0.8,       # variability at rest
        "min_rest": 95.0,      # lower normal SpO₂
        "max_rest": 100.0,     # upper physiological SpO₂
        "abs_min": 20.0,       # irreversible brain damage
        "abs_max": 100.0,      # saturation ceiling
        "mean_activity": 98.0, # average during exercise
        "mean_sleep": 96.5     # slight drop during sleep
    },
    "breathing_rate": {
        "mean_rest": 16.0,     # average at rest (breaths/min)
        "std_rest": 1.3,       # variability at rest
        "min_rest": 12.0,      # lower normal rate
        "max_rest": 20.0,      # upper normal rate
        "abs_min": 4.0,        # ventilatory failure
        "abs_max": 60.0,       # severe hyperventilation
        "mean_activity": 24.0, # average during exercise
        "mean_sleep": 12.0     # slower breathing during sleep
    },
    "blood_pressure_systolic": {
        "mean_rest": 105.0,    # average at rest (mmHg)
        "std_rest": 5.0,       # variability at rest
        "min_rest": 90.0,      # lower normal systolic BP
        "max_rest": 120.0,     # upper normal systolic BP
        "abs_min": 50.0,       # lethal hypotension
        "abs_max": 300.0,      # catastrophic hypertension
        "mean_activity": 150.0,# higher due to cardiac output
        "mean_sleep": 95.0     # nocturnal BP drop
    },
    "blood_pressure_diastolic": {
        "mean_rest": 70.0,     # average at rest (mmHg)
        "std_rest": 3.3,       # variability at rest
        "min_rest": 60.0,      # lower normal diastolic BP
        "max_rest": 80.0,      # upper normal diastolic BP
        "abs_min": 30.0,       # lethal hypotension
        "abs_max": 200.0,      # catastrophic hypertension
        "mean_activity": 70.0, # little variation in exercise
        "mean_sleep": 60.0     # nocturnal BP drop
    },
    "body_temperature": {
        "mean_rest": 36.7,     # average at rest (°C)
        "std_rest": 0.2,       # variability at rest
        "min_rest": 36.1,      # lower normal temperature
        "max_rest": 37.2,      # upper normal temperature
        "abs_min": 21.0,       # lethal hypothermia (extreme cases ~11°C)
        "abs_max": 50.0,       # lethal hyperthermia (extreme cases ~46.5°C)
        "mean_activity": 38.0, # thermogenesis during exercise
        "mean_sleep": 36.4     # circadian temperature nadir
    }
}

# UI Configuration Constants
DEFAULT_DISPERSION: float = 0.1
UI_REFRESH_INTERVAL_SECONDS: int = 10
AUTO_REFRESH_CHECK_INTERVAL_SECONDS: int = 5

# Health parameter mapping for slider keys to parameter keys
SLIDER_TO_PARAM_MAPPING: Dict[str, str] = {
    "heart_rate": "heart_rate",
    "oxygen_saturation": "oxygen_saturation", 
    "breathing_rate": "breathing_rate",
    "systolic_bp": "blood_pressure_systolic",
    "diastolic_bp": "blood_pressure_diastolic",
    "body_temperature": "body_temperature"
}