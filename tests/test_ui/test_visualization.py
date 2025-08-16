"""Tests for visualization functions."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import plotly.graph_objects as go

from src.app.ui.visualization import (
    create_radial_scatter_plot,
    _add_user_point_to_plot
)
from src.app.constants import HEALTH_PARAMS


class TestCreateRadialScatterPlot:
    """Test cases for create_radial_scatter_plot function."""

    def test_create_radial_scatter_plot_basic(self):
        """Test basic scatter plot creation."""
        # Create sample data
        df = pd.DataFrame({
            "heart_rate": [80, 85, 75, 90],
            "body_temperature": [36.7, 36.8, 36.6, 36.9]
        })
        
        fig = create_radial_scatter_plot(df)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 2  # Should have health data + perfect health marker
        
        # Check that the figure has the expected layout elements
        assert fig.layout.height == 600
        # Verify figure is properly created (no title since we removed it)
        assert fig.layout.title is None or fig.layout.title.text is None

    def test_create_radial_scatter_plot_with_user_point(self):
        """Test scatter plot creation with user point."""
        df = pd.DataFrame({
            "heart_rate": [80, 85, 75, 90],
            "body_temperature": [36.7, 36.8, 36.6, 36.9]
        })
        
        user_point = {
            "heart_rate": 95.0,
            "body_temperature": 37.0
        }
        
        fig = create_radial_scatter_plot(df, user_point)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 3  # Should have data points + user point + perfect health marker
        
        # Check that user point trace exists
        trace_names = [trace.name for trace in fig.data]
        assert "Last Reading" in trace_names

    def test_create_radial_scatter_plot_single_column(self):
        """Test scatter plot creation with single column."""
        df = pd.DataFrame({
            "heart_rate": [80, 85, 75, 90, 82, 88]
        })
        
        fig = create_radial_scatter_plot(df)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 1

    def test_create_radial_scatter_plot_all_health_params(self):
        """Test scatter plot creation with all health parameters."""
        # Create data with all health parameters
        n_points = 10
        data = {}
        for param_name, param_spec in HEALTH_PARAMS.items():
            mean = param_spec["mean_rest"]
            std = param_spec["std_rest"]
            data[param_name] = np.random.normal(mean, std, n_points)
        
        df = pd.DataFrame(data)
        
        fig = create_radial_scatter_plot(df)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 1

    def test_create_radial_scatter_plot_empty_dataframe(self):
        """Test behavior with empty dataframe."""
        df = pd.DataFrame()
        
        with pytest.raises((ValueError, KeyError)):
            create_radial_scatter_plot(df)

    def test_create_radial_scatter_plot_layout_properties(self):
        """Test that plot layout has correct properties."""
        df = pd.DataFrame({
            "heart_rate": [80, 85, 75],
            "body_temperature": [36.7, 36.8, 36.6]
        })
        
        fig = create_radial_scatter_plot(df)
        
        # Check layout properties
        assert fig.layout.xaxis.scaleanchor == "y"
        assert fig.layout.xaxis.scaleratio == 1
        assert fig.layout.hovermode == "closest"
        assert fig.layout.height == 600
        assert fig.layout.legend.x == 0.98  # Legend moved to upper-right
        assert fig.layout.legend.y == 0.98

    @patch('src.app.ui.visualization.create_artificial_center_points')
    def test_create_radial_scatter_plot_uses_artificial_points(self, mock_create_points):
        """Test that artificial center points are used."""
        mock_create_points.return_value = [(0, 0.1), (1.57, 0.2)]
        
        df = pd.DataFrame({
            "heart_rate": [80, 85],
            "body_temperature": [36.7, 36.8]
        })
        
        fig = create_radial_scatter_plot(df)
        
        mock_create_points.assert_called_once_with(num_points=500)
        assert isinstance(fig, go.Figure)

    def test_create_radial_scatter_plot_hover_data(self):
        """Test that hover data is properly configured."""
        df = pd.DataFrame({
            "heart_rate": [80],
            "body_temperature": [36.7]
        })
        
        fig = create_radial_scatter_plot(df)
        
        # Check that hover template is configured
        main_trace = fig.data[0]
        assert main_trace.hovertemplate is not None
        assert "Health Data Point" in main_trace.hovertemplate
        assert "Distance from Mean" in main_trace.hovertemplate


class TestAddUserPointToPlot:
    """Test cases for _add_user_point_to_plot function."""

    def test_add_user_point_to_plot(self):
        """Test adding user point to existing plot."""
        fig = go.Figure()
        
        df = pd.DataFrame({
            "heart_rate": [80, 85, 75],
            "body_temperature": [36.7, 36.8, 36.6]
        })
        
        user_point = {
            "heart_rate": 90.0,
            "body_temperature": 37.0
        }
        
        # Mock the scaler
        mock_scaler = MagicMock()
        parameter_names = ["heart_rate", "body_temperature"]
        
        with patch('src.app.ui.visualization.calculate_radial_distance') as mock_calc:
            mock_calc.return_value = 2.5
            
            _add_user_point_to_plot(fig, user_point, df, mock_scaler, parameter_names)
            
            mock_calc.assert_called_once()
            assert len(fig.data) == 1  # Should have added one trace
            
            # Check user point trace properties
            user_trace = fig.data[0]
            assert user_trace.name == "Last Reading"
            assert user_trace.marker.color == "red"
            assert user_trace.marker.size == 12

    def test_add_user_point_to_plot_hover_template(self):
        """Test that user point has correct hover template."""
        fig = go.Figure()
        
        df = pd.DataFrame({
            "heart_rate": [80],
            "body_temperature": [36.7]
        })
        
        user_point = {
            "heart_rate": 90.0,
            "body_temperature": 37.0
        }
        
        mock_scaler = MagicMock()
        parameter_names = ["heart_rate", "body_temperature"]
        
        with patch('src.app.ui.visualization.calculate_radial_distance') as mock_calc:
            mock_calc.return_value = 2.5
            
            _add_user_point_to_plot(fig, user_point, df, mock_scaler, parameter_names)
            
            user_trace = fig.data[0]
            assert "User Input Point" in user_trace.hovertemplate
            assert "Distance from Mean" in user_trace.hovertemplate

    def test_add_user_point_to_plot_position_calculation(self):
        """Test that user point position is calculated correctly."""
        fig = go.Figure()
        
        df = pd.DataFrame({
            "heart_rate": [80],
            "body_temperature": [36.7]
        })
        
        user_point = {
            "heart_rate": 90.0,
            "body_temperature": 37.0
        }
        
        mock_scaler = MagicMock()
        parameter_names = ["heart_rate", "body_temperature"]
        
        with patch('src.app.ui.visualization.calculate_radial_distance') as mock_calc:
            mock_calc.return_value = 2.5
            
            with patch('numpy.random.default_rng') as mock_rng:
                mock_generator = MagicMock()
                mock_generator.uniform.return_value = 1.57  # π/2 radians
                mock_rng.return_value = mock_generator
                
                _add_user_point_to_plot(fig, user_point, df, mock_scaler, parameter_names)
                
                # Check that position was calculated
                user_trace = fig.data[0]
                assert len(user_trace.x) == 1
                assert len(user_trace.y) == 1
                
                # With distance=2.5 and angle=π/2, x should be ~0, y should be ~2.5
                assert abs(user_trace.x[0]) < 0.1  # cos(π/2) ≈ 0
                assert abs(user_trace.y[0] - 2.5) < 0.1  # sin(π/2) ≈ 1


if __name__ == "__main__":
    pytest.main([__file__])