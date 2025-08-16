"""Visualization functions for health sensor data.

This module provides plotting functions for health data visualization,
including radial scatter plots and distance calculations.
"""

import numpy as np
import plotly.graph_objects as go
from typing import Dict, Optional, Tuple
import pandas as pd

from src.app.utils.math_utils import (
    calculate_radial_distance,
    create_artificial_center_points
)


def create_radial_scatter_plot(
    df: pd.DataFrame, 
    user_point: Optional[Dict[str, float]] = None
) -> go.Figure:
    """Create an interactive radial scatter plot showing health data distribution.
    
    This visualization maps 6-dimensional health data to a 2D radial plot where
    distance from center represents the Mahalanobis-like distance from the mean
    health parameters.
    
    Args:
        df: DataFrame containing health parameter columns
        user_point: Optional dictionary with health parameter values for user input
        
    Returns:
        Interactive Plotly figure showing health data distribution
    """
    from sklearn.preprocessing import StandardScaler
    
    # Data preparation - extract column names and values
    parameter_names = list(df.columns)
    health_data_matrix = df[parameter_names].values
    
    # Standardize data to z-scores for equal parameter weighting
    scaler = StandardScaler()
    standardized_data = scaler.fit_transform(health_data_matrix)
    radial_distances = np.linalg.norm(standardized_data, axis=1)
    
    # Create artificial center points to show proper distribution density
    # This addresses the "curse of dimensionality" visualization issue
    rng = np.random.default_rng(42)  # Fixed seed for reproducibility
    
    center_points = create_artificial_center_points(num_points=500)
    center_r = np.array([point[1] for point in center_points])
    center_theta = np.array([point[0] for point in center_points])
    center_x = center_r * np.cos(center_theta)
    center_y = center_r * np.sin(center_theta)
    
    # Convert original data points to polar coordinates
    original_theta = rng.uniform(0, 2 * np.pi, size=len(health_data_matrix))
    original_x = radial_distances * np.cos(original_theta)
    original_y = radial_distances * np.sin(original_theta)
    
    # Combine original and artificial center points
    all_x = np.concatenate([original_x, center_x])
    all_y = np.concatenate([original_y, center_y])
    all_radii = np.concatenate([radial_distances, center_r])
    
    # Prepare hover data (pad center points with mean values)
    center_data = np.tile(df.mean().values, (len(center_points), 1))
    all_health_data = np.concatenate([health_data_matrix, center_data])
    hover_data = np.column_stack([all_radii, all_health_data])
    
    # Create hover template with health parameter details
    hover_template = (
        "<b>Health Data Point</b><br>"
        "Distance from Mean: %{customdata[0]:.2f}<br>" +
        "<br>".join([
            f"{param}=%{{customdata[{i+1}]:.2f}}" 
            for i, param in enumerate(parameter_names)
        ]) +
        "<extra></extra>"
    )
    
    # Initialize the plot figure
    fig = go.Figure()
    
    # Add main health data points (lighter blue color)
    fig.add_trace(go.Scatter(
        x=all_x, 
        y=all_y, 
        mode="markers", 
        name="Health Data",
        marker=dict(size=6, color="#4A90E2", opacity=0.6),
        customdata=hover_data,
        text=["Health Reading"] * len(all_x),
        hovertemplate=hover_template
    ))
    
    # Add user input point if provided
    if user_point is not None:
        _add_user_point_to_plot(fig, user_point, df, scaler, parameter_names)
    
    # Add center marker for "perfect health" at origin (0,0)
    fig.add_trace(go.Scatter(
        x=[0], 
        y=[0], 
        mode="markers", 
        name="Perfect Health",
        marker=dict(
            size=14, 
            color="darkgreen", 
            symbol="cross",
            line=dict(width=1, color="#FFFFFF")
        ),
        text=["Perfect Health Center"],
        hovertemplate="<b>Perfect Health Center</b><br>Distance: 0.00<extra></extra>"
    ))
    
    # Configure plot layout (remove title, move legend to upper-right)
    fig.update_layout(
        xaxis_title="x = r · cos(θ)",
        yaxis_title="y = r · sin(θ)",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        legend=dict(x=0.98, y=0.98, xanchor="right", yanchor="top"),
        hovermode="closest",
        height=600
    )
    
    return fig


def _add_user_point_to_plot(
    fig: go.Figure,
    user_point: Dict[str, float],
    reference_df: pd.DataFrame,
    scaler,
    parameter_names: list
) -> None:
    """Add user input point to the existing plot.
    
    Args:
        fig: Plotly figure to add the point to
        user_point: Dictionary of user health parameter values
        reference_df: Reference DataFrame for calculating distance  
        scaler: Fitted StandardScaler for data normalization
        parameter_names: List of health parameter names
    """
    # Calculate radial distance for user point
    user_distance = calculate_radial_distance(
        user_point, 
        {param: reference_df[param].mean() for param in parameter_names}
    )
    
    # Position user point at consistent angle
    user_theta = np.random.default_rng(123).uniform(0, 2 * np.pi)
    user_x = user_distance * np.cos(user_theta)
    user_y = user_distance * np.sin(user_theta)
    
    # Prepare hover data for user point
    user_values = [user_point[param] for param in parameter_names]
    user_hover_data = np.array([[user_distance] + user_values])
    
    user_hover_template = (
        "<b>User Input Point</b><br>"
        "Distance from Mean: %{customdata[0]:.2f}<br>" +
        "<br>".join([
            f"{param}=%{{customdata[{i+1}]:.2f}}" 
            for i, param in enumerate(parameter_names)
        ]) +
        "<extra></extra>"
    )
    
    # Add user point to plot (slightly larger for visibility)
    fig.add_trace(go.Scatter(
        x=[user_x], 
        y=[user_y], 
        mode="markers", 
        name="Last Reading",
        marker=dict(size=12, color="red", opacity=0.9),
        customdata=user_hover_data,
        text=["Last Reading"],
        hovertemplate=user_hover_template
    ))