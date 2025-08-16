"""Tests for mathematical utility functions."""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from src.app.utils.math_utils import (
    calculate_radial_distance,
    apply_variance_to_health_data,
    create_artificial_center_points,
    validate_health_parameter_ranges
)
from src.app.constants import HEALTH_PARAMS


class TestCalculateRadialDistance:
    """Test cases for calculate_radial_distance function."""

    def test_calculate_radial_distance_identical_points(self):
        """Test that identical points have zero distance."""
        data_point = {"heart_rate": 80.0, "body_temperature": 36.7}
        center_point = {"heart_rate": 80.0, "body_temperature": 36.7}
        
        distance = calculate_radial_distance(data_point, center_point)
        
        assert distance == pytest.approx(0.0, abs=1e-10)

    def test_calculate_radial_distance_different_points(self):
        """Test distance calculation between different points."""
        data_point = {"heart_rate": 85.0, "body_temperature": 37.0}
        center_point = {"heart_rate": 80.0, "body_temperature": 36.7}
        
        distance = calculate_radial_distance(data_point, center_point)
        
        assert distance > 0.0
        assert isinstance(distance, float)

    def test_calculate_radial_distance_single_parameter(self):
        """Test distance calculation with single parameter."""
        data_point = {"heart_rate": 90.0}
        center_point = {"heart_rate": 80.0}
        
        distance = calculate_radial_distance(data_point, center_point)
        
        assert distance > 0.0

    def test_calculate_radial_distance_multiple_parameters(self):
        """Test distance calculation with multiple parameters."""
        data_point = {
            "heart_rate": 90.0,
            "oxygen_saturation": 95.0,
            "body_temperature": 37.0
        }
        center_point = {
            "heart_rate": 80.0,
            "oxygen_saturation": 97.5,
            "body_temperature": 36.7
        }
        
        distance = calculate_radial_distance(data_point, center_point)
        
        assert distance > 0.0
        assert isinstance(distance, float)

    def test_calculate_radial_distance_empty_points(self):
        """Test behavior with empty dictionaries."""
        data_point = {}
        center_point = {}
        
        with pytest.raises(ValueError):
            calculate_radial_distance(data_point, center_point)


class TestApplyVarianceToHealthData:
    """Test cases for apply_variance_to_health_data function."""

    def test_apply_variance_zero_multiplier(self):
        """Test that zero variance multiplier returns original values."""
        base_values = {"heart_rate": 80.0, "body_temperature": 36.7}
        variance_params = {"heart_rate": 6.7, "body_temperature": 0.2}
        variance_multiplier = 0.0
        
        result = apply_variance_to_health_data(base_values, variance_params, variance_multiplier)
        
        assert result["heart_rate"] == 80.0
        assert result["body_temperature"] == 36.7

    def test_apply_variance_with_multiplier(self):
        """Test variance application with non-zero multiplier."""
        base_values = {"heart_rate": 80.0}
        variance_params = {"heart_rate": 6.7}
        variance_multiplier = 1.0
        
        # Mock random number generator for predictable results
        with patch('numpy.random.default_rng') as mock_rng:
            mock_generator = MagicMock()
            mock_generator.normal.return_value = 85.0
            mock_rng.return_value = mock_generator
            
            result = apply_variance_to_health_data(base_values, variance_params, variance_multiplier)
            
            mock_generator.normal.assert_called_once_with(80.0, 6.7)
            assert result["heart_rate"] == 85.0

    def test_apply_variance_missing_variance_param(self):
        """Test behavior when variance parameter is missing."""
        base_values = {"heart_rate": 80.0, "unknown_param": 50.0}
        variance_params = {"heart_rate": 6.7}
        variance_multiplier = 1.0
        
        result = apply_variance_to_health_data(base_values, variance_params, variance_multiplier)
        
        assert "heart_rate" in result
        assert "unknown_param" in result
        assert result["unknown_param"] == 50.0  # Should keep original value

    def test_apply_variance_empty_inputs(self):
        """Test behavior with empty inputs."""
        result = apply_variance_to_health_data({}, {}, 1.0)
        assert result == {}

    @pytest.mark.parametrize("multiplier", [0.0, 0.5, 1.0, 2.0])
    def test_apply_variance_different_multipliers(self, multiplier):
        """Test variance application with different multipliers."""
        base_values = {"heart_rate": 80.0}
        variance_params = {"heart_rate": 6.7}
        
        result = apply_variance_to_health_data(base_values, variance_params, multiplier)
        
        assert isinstance(result["heart_rate"], float)
        if multiplier == 0.0:
            assert result["heart_rate"] == 80.0


class TestCreateArtificialCenterPoints:
    """Test cases for create_artificial_center_points function."""

    def test_create_artificial_center_points_default(self):
        """Test creation of artificial center points with default parameters."""
        points = create_artificial_center_points()
        
        assert len(points) == 50  # Default number
        assert all(len(point) == 2 for point in points)  # (theta, distance) tuples
        assert all(isinstance(point[0], float) and isinstance(point[1], float) for point in points)

    def test_create_artificial_center_points_custom_count(self):
        """Test creation of artificial center points with custom count."""
        custom_count = 100
        points = create_artificial_center_points(num_points=custom_count)
        
        assert len(points) == custom_count

    def test_create_artificial_center_points_angle_range(self):
        """Test that angles are within valid range [0, 2π]."""
        points = create_artificial_center_points(num_points=10)
        
        for theta, distance in points:
            assert 0 <= theta <= 2 * np.pi

    def test_create_artificial_center_points_distance_positive(self):
        """Test that distances are positive."""
        points = create_artificial_center_points(num_points=10)
        
        for theta, distance in points:
            assert distance >= 0

    def test_create_artificial_center_points_reproducibility(self):
        """Test that function produces reproducible results."""
        points1 = create_artificial_center_points(num_points=10)
        points2 = create_artificial_center_points(num_points=10)
        
        # Should be identical due to fixed random seed
        assert points1 == points2


class TestValidateHealthParameterRanges:
    """Test cases for validate_health_parameter_ranges function."""

    def test_validate_health_parameter_ranges_valid_data(self):
        """Test validation with valid health data."""
        health_data = {
            "heart_rate": 80.0,
            "oxygen_saturation": 97.5,
            "body_temperature": 36.7
        }
        
        result = validate_health_parameter_ranges(health_data, HEALTH_PARAMS)
        
        assert result["heart_rate"] is True
        assert result["oxygen_saturation"] is True
        assert result["body_temperature"] is True

    def test_validate_health_parameter_ranges_invalid_data(self):
        """Test validation with invalid health data."""
        health_data = {
            "heart_rate": 200.0,  # Too high
            "oxygen_saturation": 85.0,  # Too low
            "body_temperature": 36.7  # Valid
        }
        
        result = validate_health_parameter_ranges(health_data, HEALTH_PARAMS)
        
        assert result["heart_rate"] is False
        assert result["oxygen_saturation"] is False
        assert result["body_temperature"] is True

    def test_validate_health_parameter_ranges_boundary_values(self):
        """Test validation with boundary values."""
        health_data = {
            "heart_rate": 60.0,  # At min_rest
            "oxygen_saturation": 100.0,  # At max_rest
        }
        
        result = validate_health_parameter_ranges(health_data, HEALTH_PARAMS)
        
        assert result["heart_rate"] is True
        assert result["oxygen_saturation"] is True

    def test_validate_health_parameter_ranges_unknown_parameter(self):
        """Test validation with unknown parameter."""
        health_data = {
            "unknown_param": 50.0,
            "heart_rate": 80.0
        }
        
        result = validate_health_parameter_ranges(health_data, HEALTH_PARAMS)
        
        assert result["unknown_param"] is False
        assert result["heart_rate"] is True

    def test_validate_health_parameter_ranges_empty_data(self):
        """Test validation with empty health data."""
        result = validate_health_parameter_ranges({}, HEALTH_PARAMS)
        assert result == {}

    def test_validate_health_parameter_ranges_missing_spec(self):
        """Test validation when parameter spec is incomplete."""
        health_data = {"test_param": 50.0}
        incomplete_specs = {"test_param": {}}  # Missing min_rest, max_rest
        
        result = validate_health_parameter_ranges(health_data, incomplete_specs)
        
        # Should be valid when no limits are specified
        assert result["test_param"] is True


if __name__ == "__main__":
    pytest.main([__file__])