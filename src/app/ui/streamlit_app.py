"""Streamlit Health Sensor Simulator App.

This module provides the main Streamlit user interface for the health sensor
simulator, including interactive controls and real-time data visualization.
"""

import logging
import logging.config
import streamlit as st
import time
from typing import Dict

from src.app.config import get_settings
from src.app.services.data_simulator import generate_dummy_data, get_shared_data_generator, store_current_health_point
from src.app.services.anomaly_detector import detect_anomaly
from src.app.ui.config import SLIDER_CONFIG, DEFAULT_DISPERSION
from src.app.ui.helpers import create_slider
from src.app.ui.visualization import create_radial_scatter_plot
from src.app.constants import UI_REFRESH_INTERVAL_SECONDS

# Configure logging for Streamlit subprocess
settings = get_settings()
logging.config.dictConfig(settings.get_logging_config())

st.set_page_config(
    page_title="Health Sensor Simulator",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "This is a health sensor simulator app that performs anomaly detection in generated data."}
)

@st.cache_data
def get_dummy_dataset():
    """Generate and cache the dummy dataset for background visualization.
    
    This dataset provides context points showing the normal health parameter ranges
    and is cached to improve performance since it doesn't need to change frequently.
    
    Returns:
        DataFrame: Cached dummy health dataset
    """
    return generate_dummy_data()

# Initialize session state and data generator (use shared instance)
if 'data_generator' not in st.session_state:
    st.session_state.data_generator = get_shared_data_generator()
if 'last_auto_update' not in st.session_state:
    st.session_state.last_auto_update = time.time()

# Page setup
st.title("Health Sensor Simulator")

# Sidebar: Health parameter sliders
container_vitals = st.sidebar.container(border=True)
container_vitals.write("Set Vitals")
health_values: Dict[str, float] = {}
for key, config in SLIDER_CONFIG.items():
    health_values[key] = create_slider(container_vitals, config)

# Sidebar: Dispersion control (separated section)
st.sidebar.write("")  # Add space
st.sidebar.write("")  # Add space
st.sidebar.write("")  # Add space
# Initialize dispersion if not exists
if 'dispersion' not in st.session_state:
    st.session_state.dispersion = DEFAULT_DISPERSION
dispersion = st.sidebar.slider("Values Dispersion", 0.0, 1.0, key="dispersion", help="Adjust the dispersion of health values to simulate variability in sensor readings.")

# Sidebar: Reset button
if st.sidebar.button("Reset", use_container_width=True, type="primary"):
    # Clear all slider values to reset to defaults
    keys_to_clear = ['dispersion'] + [config['session_key'] for config in SLIDER_CONFIG.values()]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Generate health data point
data_generator = st.session_state.data_generator
current_time = time.time()
time_since_last_update = current_time - st.session_state.last_auto_update

# Check if we need to generate a new point and update timestamp
should_refresh = False
if time_since_last_update >= data_generator.settings.DATA_GENERATION_INTERVAL_SECONDS:
    health_point = data_generator.generate_new_health_point(health_values, dispersion)
    st.session_state.last_auto_update = current_time
    should_refresh = True
else:
    health_point = data_generator.get_current_health_point(health_values, dispersion)

# Store the generated health point in shared memory for API access
store_current_health_point(health_point)


# Display visualization
health_dataset = get_dummy_dataset()
visualization_figure = create_radial_scatter_plot(health_dataset, health_point)
st.plotly_chart(visualization_figure, use_container_width=True)

# Add explanatory text below the plot
st.caption("Distance from center shows health deviation. Angle is for display only and does not convey information.")

# Anomaly detection and alarm component
alarm_placeholder = st.empty()
is_anomaly, anomaly_score = detect_anomaly(health_point)
if is_anomaly:
    alarm_placeholder.warning(f"⚠️ Health Anomaly Detected. Probability: {anomaly_score:.1%}. Consult a professional.")
else:
    alarm_placeholder.empty()

# Single auto-refresh point
if should_refresh:
    st.rerun()
elif time_since_last_update < data_generator.settings.DATA_GENERATION_INTERVAL_SECONDS:
    time.sleep(UI_REFRESH_INTERVAL_SECONDS)
    st.rerun()