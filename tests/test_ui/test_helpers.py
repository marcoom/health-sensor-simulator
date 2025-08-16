"""Tests for UI helper functions."""

import pytest
from unittest.mock import patch, MagicMock

from src.app.ui.helpers import (
    create_slider
)
from src.app.ui.config import SLIDER_CONFIG
from src.app.constants import HEALTH_PARAMS




class TestCreateSlider:
    """Test cases for create_slider function."""

    @patch('src.app.ui.helpers.st')
    def test_create_slider_new_session_key(self, mock_st):
        """Test slider creation when session key doesn't exist."""
        mock_container = MagicMock()
        mock_st.session_state = {}
        
        config = {
            "param_key": "heart_rate",
            "session_key": "heart_rate",
            "label": "Heart Rate [bpm]",
            "type": int
        }
        
        # Mock the slider return value
        mock_container.slider.return_value = 80
        
        result = create_slider(mock_container, config)
        
        # Check that session state was initialized
        expected_default = HEALTH_PARAMS["heart_rate"]["mean_rest"]
        assert mock_st.session_state["heart_rate"] == expected_default
        
        # Check that slider was called with correct parameters
        mock_container.slider.assert_called_once()
        call_args = mock_container.slider.call_args
        
        assert call_args[0][0] == "Heart Rate [bpm]"  # label
        assert call_args[1]["min_value"] == int(HEALTH_PARAMS["heart_rate"]["min_rest"])
        assert call_args[1]["max_value"] == int(HEALTH_PARAMS["heart_rate"]["max_rest"])
        assert call_args[1]["key"] == "heart_rate"
        
        assert result == 80

    @patch('src.app.ui.helpers.st')
    def test_create_slider_existing_session_key(self, mock_st):
        """Test slider creation when session key already exists."""
        mock_container = MagicMock()
        mock_st.session_state = {"heart_rate": 90.0}
        
        config = {
            "param_key": "heart_rate",
            "session_key": "heart_rate",
            "label": "Heart Rate [bpm]",
            "type": int
        }
        
        mock_container.slider.return_value = 90
        
        result = create_slider(mock_container, config)
        
        # Should not overwrite existing session state
        assert mock_st.session_state["heart_rate"] == 90.0
        assert result == 90

    @patch('src.app.ui.helpers.st')
    def test_create_slider_float_type(self, mock_st):
        """Test slider creation with float type includes step parameter."""
        mock_container = MagicMock()
        mock_st.session_state = {}
        
        config = {
            "param_key": "body_temperature",
            "session_key": "body_temperature",
            "label": "Body Temperature [°C]",
            "type": float
        }
        
        mock_container.slider.return_value = 36.7
        
        create_slider(mock_container, config)
        
        # Check that step parameter was added for float type
        call_args = mock_container.slider.call_args
        assert call_args[1]["step"] == 0.1

    @patch('src.app.ui.helpers.st')
    def test_create_slider_int_type(self, mock_st):
        """Test slider creation with int type doesn't include step parameter."""
        mock_container = MagicMock()
        mock_st.session_state = {}
        
        config = {
            "param_key": "heart_rate",
            "session_key": "heart_rate",
            "label": "Heart Rate [bpm]",
            "type": int
        }
        
        create_slider(mock_container, config)
        
        # Check that step parameter was not added for int type
        call_args = mock_container.slider.call_args
        assert "step" not in call_args[1]

    @patch('src.app.ui.helpers.st')
    def test_create_slider_all_parameters(self, mock_st):
        """Test slider creation validates all health parameters."""
        mock_container = MagicMock()
        mock_st.session_state = {}
        
        for slider_key, config in SLIDER_CONFIG.items():
            mock_container.reset_mock()
            mock_container.slider.return_value = 50  # Dummy return value
            
            result = create_slider(mock_container, config)
            
            # Check that slider was called
            mock_container.slider.assert_called_once()
            
            # Check that session state was initialized
            session_key = config["session_key"]
            param_key = config["param_key"]
            value_type = config["type"]
            expected_value = value_type(HEALTH_PARAMS[param_key]["mean_rest"])
            assert session_key in mock_st.session_state
            assert mock_st.session_state[session_key] == expected_value




if __name__ == "__main__":
    pytest.main([__file__])