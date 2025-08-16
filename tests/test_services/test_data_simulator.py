"""Tests for data simulation services."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

from src.app.services.data_simulator import (
    generate_dummy_data,
    generate_health_point_with_variance,
    HealthDataGenerator
)
from src.app.constants import HEALTH_PARAMS


class TestGenerateDummyData:
    """Test cases for generate_dummy_data function."""

    def test_generate_dummy_data_default_size(self):
        """Test that dummy data is generated with default size."""
        df = generate_dummy_data()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1000  # Default size
        assert list(df.columns) == list(HEALTH_PARAMS.keys())

    def test_generate_dummy_data_custom_size(self):
        """Test that dummy data is generated with custom size."""
        custom_size = 500
        df = generate_dummy_data(dataset_size=custom_size)
        
        assert len(df) == custom_size
        assert isinstance(df, pd.DataFrame)

    def test_generate_dummy_data_column_names(self):
        """Test that generated data has correct column names."""
        df = generate_dummy_data()
        expected_columns = set(HEALTH_PARAMS.keys())
        actual_columns = set(df.columns)
        
        assert actual_columns == expected_columns

    def test_generate_dummy_data_value_ranges(self):
        """Test that generated values are within reasonable ranges."""
        df = generate_dummy_data()
        
        for param_name in HEALTH_PARAMS.keys():
            param_spec = HEALTH_PARAMS[param_name]
            values = df[param_name]
            
            # Check that values are roughly centered around mean_rest
            mean_diff = abs(values.mean() - param_spec["mean_rest"])
            assert mean_diff < param_spec["std_rest"]  # Should be close to expected mean
            
            # Check that standard deviation is reasonable
            std_diff = abs(values.std() - param_spec["std_rest"])
            assert std_diff < param_spec["std_rest"] * 0.5  # Within 50% of expected std


class TestGenerateHealthPointWithVariance:
    """Test cases for generate_health_point_with_variance function."""

    def test_generate_health_point_basic(self):
        """Test basic health point generation."""
        health_values = {
            "heart_rate": 80.0,
            "oxygen_saturation": 97.5,
            "breathing_rate": 16.0,
            "systolic_bp": 105.0,
            "diastolic_bp": 70.0,
            "body_temperature": 36.7
        }
        variance_multiplier = 0.0  # No variance
        
        result = generate_health_point_with_variance(health_values, variance_multiplier)
        
        assert isinstance(result, dict)
        assert len(result) == len(health_values)
        
        # With no variance, values should be exactly the input values
        for slider_key, input_value in health_values.items():
            param_key = health_values.keys().__iter__().__next__()  # Get first key for mapping
            assert abs(result[f"blood_pressure_systolic" if slider_key == "systolic_bp" else 
                             f"blood_pressure_diastolic" if slider_key == "diastolic_bp" else slider_key] - input_value) < 0.1

    def test_generate_health_point_with_variance(self):
        """Test health point generation with variance applied."""
        health_values = {
            "heart_rate": 80.0,
            "oxygen_saturation": 97.5,
            "breathing_rate": 16.0,
            "systolic_bp": 105.0,
            "diastolic_bp": 70.0,
            "body_temperature": 36.7
        }
        variance_multiplier = 1.0  # Full variance
        
        result = generate_health_point_with_variance(health_values, variance_multiplier)
        
        assert isinstance(result, dict)
        assert len(result) == len(health_values)
        
        # Check that parameter mapping worked correctly
        assert "heart_rate" in result
        assert "oxygen_saturation" in result
        assert "breathing_rate" in result
        assert "blood_pressure_systolic" in result
        assert "blood_pressure_diastolic" in result
        assert "body_temperature" in result

    def test_generate_health_point_empty_input(self):
        """Test behavior with empty health values."""
        health_values = {}
        variance_multiplier = 0.5
        
        result = generate_health_point_with_variance(health_values, variance_multiplier)
        
        assert isinstance(result, dict)
        assert len(result) == 0

    @pytest.mark.parametrize("variance_multiplier", [0.0, 0.5, 1.0, 2.0])
    def test_generate_health_point_different_variances(self, variance_multiplier):
        """Test health point generation with different variance levels."""
        health_values = {
            "heart_rate": 80.0,
            "body_temperature": 36.7
        }
        
        result = generate_health_point_with_variance(health_values, variance_multiplier)
        
        assert isinstance(result, dict)
        assert "heart_rate" in result
        assert "body_temperature" in result


class TestHealthDataGenerator:
    """Test cases for HealthDataGenerator class."""

    def test_health_data_generator_initialization(self):
        """Test that HealthDataGenerator initializes correctly."""
        generator = HealthDataGenerator()
        
        assert generator.settings is not None
        assert generator.last_generation_time is None
        assert generator.current_health_point is None

    def test_should_generate_new_point_first_call(self):
        """Test that should_generate_new_point returns True on first call."""
        generator = HealthDataGenerator()
        
        assert generator.should_generate_new_point() is True

    def test_should_generate_new_point_timing(self):
        """Test timing logic for should_generate_new_point."""
        generator = HealthDataGenerator()
        
        # Mock time to control timing
        with patch('time.time') as mock_time:
            mock_time.return_value = 1000.0
            
            # Set a recent generation time
            generator.last_generation_time = 999.0  # 1 second ago
            
            # Should not generate yet (less than interval)
            assert generator.should_generate_new_point() is False
            
            # Move time forward beyond interval
            mock_time.return_value = 1006.0  # 6 seconds from generation
            assert generator.should_generate_new_point() is True

    def test_generate_new_health_point(self):
        """Test generate_new_health_point method."""
        generator = HealthDataGenerator()
        health_values = {"heart_rate": 80.0}
        variance_multiplier = 0.5
        
        with patch('time.time', return_value=1000.0):
            result = generator.generate_new_health_point(health_values, variance_multiplier)
            
            assert isinstance(result, dict)
            assert generator.last_generation_time == 1000.0
            assert generator.current_health_point == result

    def test_get_current_health_point(self):
        """Test get_current_health_point method."""
        generator = HealthDataGenerator()
        health_values = {"heart_rate": 80.0}
        variance_multiplier = 0.5
        
        result = generator.get_current_health_point(health_values, variance_multiplier)
        
        assert isinstance(result, dict)
        assert "heart_rate" in result

    def test_get_time_until_next_generation(self):
        """Test get_time_until_next_generation method."""
        generator = HealthDataGenerator()
        
        # No previous generation
        assert generator.get_time_until_next_generation() == 0.0
        
        # With previous generation time
        with patch('time.time') as mock_time:
            mock_time.return_value = 1000.0
            generator.last_generation_time = 998.0  # 2 seconds ago
            
            # Should return remaining time (5 - 2 = 3 seconds)
            expected_remaining = generator.settings.DATA_GENERATION_INTERVAL_SECONDS - 2
            assert generator.get_time_until_next_generation() == expected_remaining
            
            # When time has passed beyond interval
            generator.last_generation_time = 994.0  # 6 seconds ago
            assert generator.get_time_until_next_generation() == 0.0


if __name__ == "__main__":
    pytest.main([__file__])