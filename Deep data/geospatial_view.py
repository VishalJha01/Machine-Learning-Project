import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_geospatial_view(current_aqi):
    """
    Create a geospatial view of Sohna showing the current AQI level
    
    Parameters:
    current_aqi (float): Current AQI value
    
    Returns:
    plotly.graph_objects.Figure: Plotly figure with geospatial view
    """
    
    # Sohna coordinates (approximate)
    sohna_lat = 28.2500
    sohna_center_long = 77.0700
    
    # Create color based on AQI
    if current_aqi <= 50:
        color = '#00e400'  # Good
        category = 'Good'
    elif current_aqi <= 100:
        color = '#ffff00'  # Moderate
        category = 'Moderate'
    elif current_aqi <= 150:
        color = '#ff7e00'  # Unhealthy for Sensitive Groups
        category = 'Unhealthy for Sensitive Groups'
    elif current_aqi <= 200:
        color = '#ff0000'  # Unhealthy
        category = 'Unhealthy'
    elif current_aqi <= 300:
        color = '#99004c'  # Very Unhealthy
        category = 'Very Unhealthy'
    else:
        color = '#7e0023'  # Hazardous
        category = 'Hazardous'
    
    # Create a simple map centered on Sohna
    fig = go.Figure()
    
    # Add a marker for Sohna
    fig.add_trace(go.Scattermapbox(
        lat=[sohna_lat],
        lon=[sohna_center_long],
        mode='markers',
        marker=dict(
            size=20,
            color=color,
            opacity=0.8
        ),
        text=[f"Sohna: AQI {current_aqi:.1f} ({category})"],
        hoverinfo='text'
    ))
    
    # Add a circle to represent the area affected
    # Create a circle of points around Sohna
    radius_km = 5  # 5 km radius
    points = 100  # number of points to create a smooth circle
    
    # Convert radius from km to degrees (approximate)
    radius_lat = radius_km / 111  # 1 degree latitude is approximately 111 km
    radius_long = radius_km / (111 * np.cos(np.radians(sohna_lat)))  # Adjust for longitude
    
    # Generate circle points
    circle_lats = []
    circle_longs = []
    for i in range(points + 1):
        angle = (i / points) * 2 * np.pi
        circle_lats.append(sohna_lat + radius_lat * np.sin(angle))
        circle_longs.append(sohna_center_long + radius_long * np.cos(angle))
    
    # Add the circle to the map
    fig.add_trace(go.Scattermapbox(
        lat=circle_lats,
        lon=circle_longs,
        mode='lines',
        line=dict(
            width=2,
            color=color
        ),
        hoverinfo='none'
    ))
    
    # Set up the map layout
    fig.update_layout(
        mapbox=dict(
            style="dark",
            zoom=10,
            center=dict(
                lat=sohna_lat,
                lon=sohna_center_long
            )
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    return fig