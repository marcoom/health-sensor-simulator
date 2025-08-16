"""Tests for health parameter constants."""

import pytest
from src.app.constants import (
    HEALTH_PARAMS,
    DEFAULT_DISPERSION,
    UI_REFRESH_INTERVAL_SECONDS,
    AUTO_REFRESH_CHECK_INTERVAL_SECONDS,
    SLIDER_TO_PARAM_MAPPING
)


class TestHealthParams:
    """Test cases for HEALTH_PARAMS constant."""

    def test_health_params_structure(self):
        """Test that HEALTH_PARAMS has the expected structure."""
        expected_parameters = {
            "heart_rate",
            "oxygen_saturation", 
            "breathing_rate",
            "blood_pressure_systolic",
            "blood_pressure_diastolic",
            "body_temperature"
        }
        
        assert set(HEALTH_PARAMS.keys()) == expected_parameters

    def test_health_params_required_fields(self):
        """Test that each health parameter has required fields."""
        required_fields = {
            "mean_rest", "std_rest", "min_rest", "max_rest",
            "abs_min", "abs_max", "mean_activity", "mean_sleep"
        }
        
        for param_name, param_spec in HEALTH_PARAMS.items():
            assert set(param_spec.keys()) == required_fields, f"Missing fields in {param_name}"

    def test_health_params_value_types(self):
        """Test that health parameter values are numeric."""
        for param_name, param_spec in HEALTH_PARAMS.items():
            for field_name, value in param_spec.items():
                assert isinstance(value, (int, float)), f"{param_name}.{field_name} is not numeric"

    def test_health_params_logical_ranges(self):
        """Test that health parameter ranges are logically consistent."""
        for param_name, param_spec in HEALTH_PARAMS.items():
            # Basic range consistency
            assert param_spec["min_rest"] <= param_spec["max_rest"], f"{param_name}: min_rest > max_rest"
            assert param_spec["abs_min"] <= param_spec["abs_max"], f"{param_name}: abs_min > abs_max"
            
            # Mean values should be within ranges
            assert param_spec["min_rest"] <= param_spec["mean_rest"] <= param_spec["max_rest"], \
                f"{param_name}: mean_rest outside normal range"
            
            # Standard deviation should be positive
            assert param_spec["std_rest"] > 0, f"{param_name}: std_rest should be positive"
            
            # Absolute range should encompass normal range
            assert param_spec["abs_min"] <= param_spec["min_rest"], f"{param_name}: abs_min > min_rest"
            assert param_spec["max_rest"] <= param_spec["abs_max"], f"{param_name}: max_rest > abs_max"

    def test_health_params_realistic_values(self):
        """Test that health parameter values are realistic."""
        # Heart rate checks
        hr = HEALTH_PARAMS["heart_rate"]
        assert 40 <= hr["mean_rest"] <= 120, "Heart rate mean_rest unrealistic"
        assert hr["std_rest"] < 20, "Heart rate std_rest too high"
        
        # Oxygen saturation checks
        o2 = HEALTH_PARAMS["oxygen_saturation"]
        assert 90 <= o2["mean_rest"] <= 100, "Oxygen saturation mean_rest unrealistic"
        assert o2["max_rest"] <= 100, "Oxygen saturation cannot exceed 100%"
        
        # Body temperature checks (assuming Celsius)
        temp = HEALTH_PARAMS["body_temperature"]
        assert 35 <= temp["mean_rest"] <= 38, "Body temperature mean_rest unrealistic"
        assert temp["std_rest"] < 2, "Body temperature std_rest too high"

    @pytest.mark.parametrize("param_name", list(HEALTH_PARAMS.keys()))
    def test_individual_health_params(self, param_name):
        """Test individual health parameters for completeness."""
        param_spec = HEALTH_PARAMS[param_name]
        
        # Check all required keys exist
        required_keys = ["mean_rest", "std_rest", "min_rest", "max_rest", 
                        "abs_min", "abs_max", "mean_activity", "mean_sleep"]
        for key in required_keys:
            assert key in param_spec, f"Missing {key} in {param_name}"
        
        # Check that values are reasonable
        assert param_spec["std_rest"] > 0, f"Standard deviation should be positive for {param_name}"
        assert param_spec["min_rest"] < param_spec["max_rest"], f"Range invalid for {param_name}"


class TestSliderToParamMapping:
    """Test cases for SLIDER_TO_PARAM_MAPPING constant."""

    def test_slider_to_param_mapping_completeness(self):
        """Test that slider mapping covers all health parameters."""
        mapped_params = set(SLIDER_TO_PARAM_MAPPING.values())
        health_params = set(HEALTH_PARAMS.keys())
        
        assert mapped_params == health_params, "Slider mapping doesn't cover all health parameters"

    def test_slider_to_param_mapping_uniqueness(self):
        """Test that each slider key maps to a unique parameter."""
        slider_keys = list(SLIDER_TO_PARAM_MAPPING.keys())
        param_values = list(SLIDER_TO_PARAM_MAPPING.values())
        
        assert len(slider_keys) == len(set(slider_keys)), "Duplicate slider keys"
        assert len(param_values) == len(set(param_values)), "Duplicate parameter mappings"

    def test_slider_to_param_mapping_expected_keys(self):
        """Test that expected slider keys are present."""
        expected_slider_keys = {
            "heart_rate",
            "oxygen_saturation",
            "breathing_rate", 
            "systolic_bp",
            "diastolic_bp",
            "body_temperature"
        }
        
        assert set(SLIDER_TO_PARAM_MAPPING.keys()) == expected_slider_keys

    def test_slider_to_param_mapping_blood_pressure(self):
        """Test specific blood pressure mappings."""
        assert SLIDER_TO_PARAM_MAPPING["systolic_bp"] == "blood_pressure_systolic"
        assert SLIDER_TO_PARAM_MAPPING["diastolic_bp"] == "blood_pressure_diastolic"


class TestConstantValues:
    """Test cases for other constant values."""

    def test_default_dispersion_range(self):
        """Test that DEFAULT_DISPERSION is in valid range."""
        assert 0.0 <= DEFAULT_DISPERSION <= 1.0, "DEFAULT_DISPERSION should be between 0 and 1"
        assert isinstance(DEFAULT_DISPERSION, float), "DEFAULT_DISPERSION should be float"

    def test_ui_refresh_interval(self):
        """Test that UI_REFRESH_INTERVAL_SECONDS is reasonable."""
        assert isinstance(UI_REFRESH_INTERVAL_SECONDS, int), "UI_REFRESH_INTERVAL_SECONDS should be int"
        assert 0 < UI_REFRESH_INTERVAL_SECONDS <= 10, "UI refresh interval should be reasonable"

    def test_auto_refresh_check_interval(self):
        """Test that AUTO_REFRESH_CHECK_INTERVAL_SECONDS is reasonable."""
        assert isinstance(AUTO_REFRESH_CHECK_INTERVAL_SECONDS, int), "AUTO_REFRESH_CHECK_INTERVAL_SECONDS should be int"
        assert 1 <= AUTO_REFRESH_CHECK_INTERVAL_SECONDS <= 60, "Auto refresh check interval should be reasonable"

    def test_interval_relationship(self):
        """Test logical relationship between interval constants."""
        # Both intervals should be positive values
        assert UI_REFRESH_INTERVAL_SECONDS > 0, "UI refresh interval should be positive"
        assert AUTO_REFRESH_CHECK_INTERVAL_SECONDS > 0, "Auto refresh check interval should be positive"


if __name__ == "__main__":
    pytest.main([__file__])