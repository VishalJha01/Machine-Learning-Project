import dash
from dash import dcc, html, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import requests
from io import StringIO
# Add these imports at the top of your app.py file
from forecast_model import create_forecast_model, predict_next_hours
from health_recommendations import get_health_recommendations
from geospatial_view import create_geospatial_view


# Fetch data from URL
url = "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/cleaned_sohna_aqi-3nwYgozAaJsNtEZpDWKCLOJI1BJjFN.csv"
response = requests.get(url)
data = StringIO(response.text)
df = pd.read_csv(data)

# Convert Datetime to proper datetime format
df['Datetime'] = pd.to_datetime(df['Datetime'])
df['Date'] = df['Datetime'].dt.date
df['Month'] = df['Datetime'].dt.month
df['Month_Name'] = df['Datetime'].dt.strftime('%b')
df['Day_of_Week'] = df['Datetime'].dt.day_name()
df['Hour_Num'] = df['Datetime'].dt.hour

# Convert AQI to numeric
df['AQI'] = pd.to_numeric(df['AQI'], errors='coerce')

# Create a color mapping dictionary for consistency
color_map = {
    'Good': '#00e400',
    'Moderate': '#ffff00',
    'Unhealthy for Sensitive Groups': '#ff7e00',
    'Unhealthy': '#ff0000',
    'Very Unhealthy': '#99004c',
    'Hazardous': '#7e0023'
}

# Futuristic color palette
futuristic_colors = {
    'primary': '#00f5d4',      # Bright teal
    'secondary': '#9d4edd',    # Purple
    'accent1': '#ff3864',      # Neon pink
    'accent2': '#2de2e6',      # Cyan
    'accent3': '#f6f740',      # Yellow
    'accent4': '#ff6c11',      # Orange
    'background': '#0f1020',   # Dark blue-black
    'surface': '#1a1b3a',      # Slightly lighter blue
    'text': '#ffffff',         # White
    'textSecondary': '#b3b3cc' # Light purple-gray
}

# Calculate some statistics
avg_aqi = df['AQI'].mean()
max_aqi = df['AQI'].max()
min_aqi = df['AQI'].min()

# Count occurrences of each health risk category
health_risk_counts = df['Health Risk'].value_counts().reset_index()
health_risk_counts.columns = ['Health Risk', 'Count']

# Calculate hourly averages
hourly_avg = df.groupby('Hour_Num')['AQI'].mean().reset_index()

# Calculate daily averages
daily_avg = df.groupby('Date')['AQI'].mean().reset_index()
daily_avg = daily_avg.sort_values('Date')

# Calculate monthly averages
monthly_avg = df.groupby('Month_Name')['AQI'].mean().reset_index()
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
monthly_avg['Month_Num'] = monthly_avg['Month_Name'].apply(lambda x: month_order.index(x) if x in month_order else -1)
monthly_avg = monthly_avg.sort_values('Month_Num')

# Calculate day of week averages
day_of_week_avg = df.groupby('Day_of_Week')['AQI'].mean().reset_index()
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_of_week_avg['Day_Num'] = day_of_week_avg['Day_of_Week'].apply(lambda x: day_order.index(x) if x in day_order else -1)
day_of_week_avg = day_of_week_avg.sort_values('Day_Num')

# Calculate health risk percentages for the gauge
health_percentages = health_risk_counts.copy()
health_percentages['Percentage'] = (health_percentages['Count'] / health_percentages['Count'].sum()) * 100

# Calculate recent trend (last 7 days if available)
if len(daily_avg) >= 7:
    recent_trend = daily_avg.iloc[-7:].copy()
else:
    recent_trend = daily_avg.copy()

# Get current time and find the corresponding AQI from historical data
current_hour = datetime.now().hour
current_aqi = hourly_avg[hourly_avg['Hour_Num'] == current_hour]['AQI'].values[0] if current_hour in hourly_avg['Hour_Num'].values else avg_aqi

# Determine health risk for current AQI
def get_health_risk(aqi):
    if aqi <= 50:
        return 'Good'
    elif aqi <= 100:
        return 'Moderate'
    elif aqi <= 150:
        return 'Unhealthy for Sensitive Groups'
    elif aqi <= 200:
        return 'Unhealthy'
    elif aqi <= 300:
        return 'Very Unhealthy'
    else:
        return 'Hazardous'

current_health_risk = get_health_risk(current_aqi)
# Create forecast model
forecast_model, scaler, features = create_forecast_model(df)
forecast_data = predict_next_hours(df, forecast_model, scaler, features, hours=24)

# Get health recommendations for current AQI
health_recs = get_health_recommendations(current_aqi)

# Create geospatial view
geo_fig = create_geospatial_view(current_aqi)


# Initialize the Dash app with custom CSS
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        'https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;500;600;700&family=Orbitron:wght@400;500;600;700;800;900&family=Titillium+Web:wght@200;300;400;600;700&display=swap'
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ]
)

# Set the page title
app.title = "Sohna AQI Monitoring System - 2023 Data"

# App layout
app.layout = html.Div(
    className="dashboard-container",
    children=[
        # Header
        html.Div(
            className="header",
            children=[
                html.Div(
                    className="header-content",
                    children=[
                        html.Div(
                            className="logo-container",
                            children=[
                                html.Div(className="logo-icon"),
                                html.H1("AERO·PULSE", className="title")
                            ]
                        ),
                        html.Div(
                            className="header-right",
                            children=[
                                html.Div(
                                    className="current-time",
                                    id="live-clock"
                                ),
                                html.Div(
                                    className="header-stats",
                                    children=[
                                        html.Div(
                                            className="header-stat",
                                            children=[
                                                html.Span("Current Status:", className="stat-label"),
                                                html.Div(
                                                    className="status-container",
                                                    children=[
                                                        html.Span(
                                                            f"{current_health_risk}", 
                                                            className=f"stat-value status-{current_health_risk.replace(' ', '-').lower()}"
                                                        ),
                                                        html.Div(
                                                            className="warning-icon",
                                                            style={'display': 'inline-block' if current_health_risk in ['Very Unhealthy', 'Hazardous'] else 'none'}
                                                        )
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                html.Div(
                    className="dashboard-description",
                    children=[
                        html.P([
                            "Advanced air quality monitoring system for Sohna, providing AQI analysis and health risk assessment based on 2023 data. ",
                            "Track pollution patterns, identify health risks, and make data-driven decisions with our comprehensive metrics."
                        ])
                    ]
                )
            ]
        ),
        
        # Main content
        html.Div(
            className="main-content",
            children=[
                # Left sidebar with key stats
                html.Div(
                    className="sidebar",
                    children=[
                        # Current AQI in Sohna section
                        html.Div(
                            className="sidebar-section current-aqi-section",
                            children=[
                                html.H3("Current AQI in Sohna", className="section-title"),
                                html.Div(
                                    className="current-aqi-display",
                                    children=[
                                        html.Div(
                                            className="current-aqi-value",
                                            children=[
                                                html.Span(f"{current_aqi:.1f}", className="aqi-number"),
                                                html.Span("AQI", className="aqi-unit")
                                            ]
                                        ),
                                        html.Div(
                                            className="current-aqi-status",
                                            children=[
                                                html.Span(f"{current_health_risk}", 
                                                    className=f"aqi-status-text status-{current_health_risk.replace(' ', '-').lower()}"
                                                ),
                                                html.Div(
                                                    className="warning-icon large",
                                                    style={'display': 'inline-block' if current_health_risk in ['Very Unhealthy', 'Hazardous'] else 'none'}
                                                )
                                            ]
                                        ),
                                        html.P(
                                            className="current-aqi-note",
                                            children=["Based on historical data from 2023 for this time of day"]
                                        )
                                    ]
                                )
                            ]
                        ),
                        
                        html.Div(
                            className="sidebar-section",
                            children=[
                                html.H3("Air Quality Metrics", className="section-title"),
                                html.Div(
                                    className="stat-cards",
                                    children=[
                                        html.Div(
                                            className="stat-card primary",
                                            children=[
                                                html.Div(
                                                    className="stat-icon aqi-icon"
                                                ),
                                                html.Div(
                                                    className="stat-content",
                                                    children=[
                                                        html.H4("Average AQI"),
                                                        html.Div(
                                                            className="stat-value-container",
                                                            children=[
                                                                html.Span(f"{avg_aqi:.1f}", className="stat-value"),
                                                                html.Span("units", className="stat-unit")
                                                            ]
                                                        ),
                                                        html.P("Overall air quality average")
                                                    ]
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            className="stat-card danger",
                                            children=[
                                                html.Div(
                                                    className="stat-icon max-icon"
                                                ),
                                                html.Div(
                                                    className="stat-content",
                                                    children=[
                                                        html.H4("Maximum AQI"),
                                                        html.Div(
                                                            className="stat-value-container",
                                                            children=[
                                                                html.Span(f"{max_aqi:.1f}", className="stat-value"),
                                                                html.Span("units", className="stat-unit")
                                                            ]
                                                        ),
                                                        html.P("Highest recorded value")
                                                    ]
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            className="stat-card success",
                                            children=[
                                                html.Div(
                                                    className="stat-icon min-icon"
                                                ),
                                                html.Div(
                                                    className="stat-content",
                                                    children=[
                                                        html.H4("Minimum AQI"),
                                                        html.Div(
                                                            className="stat-value-container",
                                                            children=[
                                                                html.Span(f"{min_aqi:.1f}", className="stat-value"),
                                                                html.Span("units", className="stat-unit")
                                                            ]
                                                        ),
                                                        html.P("Lowest recorded value")
                                                    ]
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            className="stat-card info",
                                            children=[
                                                html.Div(
                                                    className="stat-icon data-icon"
                                                ),
                                                html.Div(
                                                    className="stat-content",
                                                    children=[
                                                        html.H4("Data Points"),
                                                        html.Div(
                                                            className="stat-value-container",
                                                            children=[
                                                                html.Span(f"{len(df):,}", className="stat-value"),
                                                                html.Span("records", className="stat-unit")
                                                            ]
                                                        ),
                                                        html.P("Total measurements in 2023")
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        ),
                        
                        html.Div(
                            className="sidebar-section",
                            children=[
                                html.H3("Health Risk Assessment", className="section-title"),
                                html.Div(
                                    className="health-risk-container",
                                    children=[
                                        dcc.Graph(
                                            id='health-risk-gauge',
                                            figure=go.Figure(
                                                data=[
                                                    go.Pie(
                                                        values=health_percentages['Percentage'],
                                                        labels=health_percentages['Health Risk'],
                                                        hole=0.7,
                                                        textinfo='none',
                                                        hoverinfo='label+percent',
                                                        marker=dict(
                                                            colors=[color_map.get(risk, '#CCCCCC') for risk in health_percentages['Health Risk']],
                                                            line=dict(color=futuristic_colors['background'], width=1)
                                                        ),
                                                        direction='clockwise',
                                                        sort=False
                                                    )
                                                ],
                                                layout=go.Layout(
                                                    showlegend=False,
                                                    margin=dict(l=0, r=0, t=0, b=0),
                                                    paper_bgcolor='rgba(0,0,0,0)',
                                                    plot_bgcolor='rgba(0,0,0,0)',
                                                    height=220,
                                                    annotations=[
                                                        dict(
                                                            text=f"<b>{avg_aqi:.1f}</b><br>AQI",
                                                            x=0.5, y=0.5,
                                                            font=dict(size=20, color=futuristic_colors['primary']),
                                                            showarrow=False
                                                        )
                                                    ]
                                                )
                                            )
                                        ),
                                        html.Div(
                                            className="health-risk-legend",
                                            children=[
                                                html.Div(
                                                    className="legend-item",
                                                    children=[
                                                        html.Div(className="legend-color good"),
                                                        html.Div("Good", className="legend-label")
                                                    ]
                                                ),
                                                html.Div(
                                                    className="legend-item",
                                                    children=[
                                                        html.Div(className="legend-color moderate"),
                                                        html.Div("Moderate", className="legend-label")
                                                    ]
                                                ),
                                                html.Div(
                                                    className="legend-item",
                                                    children=[
                                                        html.Div(className="legend-color sensitive"),
                                                        html.Div("Unhealthy for Sensitive", className="legend-label")
                                                    ]
                                                ),
                                                html.Div(
                                                    className="legend-item",
                                                    children=[
                                                        html.Div(className="legend-color unhealthy"),
                                                        html.Div("Unhealthy", className="legend-label")
                                                    ]
                                                ),
                                                html.Div(
                                                    className="legend-item",
                                                    children=[
                                                        html.Div(className="legend-color very-unhealthy"),
                                                        html.Div("Very Unhealthy", className="legend-label")
                                                    ]
                                                ),
                                                html.Div(
                                                    className="legend-item",
                                                    children=[
                                                        html.Div(className="legend-color hazardous"),
                                                        html.Div("Hazardous", className="legend-label")
                                                    ]
                                                ),
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        
                        html.Div(
                            className="sidebar-section",
                            children=[
                                html.H3("Health Implications", className="section-title"),
                                html.Div(
                                    className="health-implications",
                                    children=[
                                        html.Div(
                                            className="implication-item",
                                            children=[
                                                html.H4("Good (0-50)"),
                                                html.P("Air quality is satisfactory, and air pollution poses little or no risk.")
                                            ]
                                        ),
                                        html.Div(
                                            className="implication-item",
                                            children=[
                                                html.H4("Moderate (51-100)"),
                                                html.P("Acceptable air quality, but some pollutants may be a concern for sensitive individuals.")
                                            ]
                                        ),
                                        html.Div(
                                            className="implication-item",
                                            children=[
                                                html.H4("Unhealthy for Sensitive Groups (101-150)"),
                                                html.P("Members of sensitive groups may experience health effects, but the general public is less likely to be affected.")
                                            ]
                                        ),
                                        html.Div(
                                            className="implication-item",
                                            children=[
                                                html.H4("Unhealthy (151-200)"),
                                                html.P("Everyone may begin to experience health effects; members of sensitive groups may experience more serious effects.")
                                            ]
                                        ),
                                        html.Div(
                                            className="implication-item very-unhealthy-item",
                                            children=[
                                                html.H4("Very Unhealthy (201-300)"),
                                                html.P("Health alert: everyone may experience more serious health effects.")
                                            ]
                                        ),
                                        html.Div(
                                            className="implication-item",
                                            children=[
                                                html.H4("Hazardous (301+)"),
                                                html.P("Health warning of emergency conditions: everyone is more likely to be affected.")
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            className="sidebar-section health-recommendations-section",
                            children=[
                                html.H3("Health Recommendations", className="section-title"),
                                html.Div(
                                    className="health-recommendation-container",
                                    children=[
                                        html.Div(
                                            className="recommendation-header",
                                            children=[
                                                html.Span(health_recs["icon"], className="recommendation-icon"),
                                                html.H4("Based on Current AQI")
                                            ]
                                        ),
                                        html.Div(
                                            className="recommendation-content",
                                            children=[
                                                html.P(health_recs["general"], className="recommendation-general"),
                                                html.H5("For Sensitive Groups:"),
                                                html.P(health_recs["sensitive_groups"]),
                                                html.H5("Outdoor Activities:"),
                                                html.P(health_recs["outdoor_activity"]),
                                                html.H5("Ventilation:"),
                                                html.P(health_recs["ventilation"]),
                                                html.H5("Mask Recommendation:"),
                                                html.P(health_recs["mask_recommendation"])
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                    ]
                ),
                
                # Main dashboard area
                html.Div(
                    className="dashboard-main",
                    children=[
                        # First row - AQI Trend
                        html.Div(
                            className="chart-row",
                            children=[
                                html.Div(
                                    className="chart-container large",
                                    children=[
                                        html.Div(
                                            className="chart-header",
                                            children=[
                                                html.H3("AQI Trend Analysis (2023)", className="chart-title"),
                                                html.Div(
                                                    className="chart-actions",
                                                    children=[
                                                        html.Div(
                                                            className="chart-action refresh",
                                                            title="Refresh Data"
                                                        ),
                                                        html.Div(
                                                            className="chart-action expand",
                                                            title="Expand"
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        dcc.Graph(
                                            id='aqi-trend-chart',
                                            className="animated-chart",
                                            figure=px.line(
                                                daily_avg, 
                                                x='Date', 
                                                y='AQI',
                                                labels={'AQI': 'Air Quality Index', 'Date': 'Date'},
                                                template='plotly_dark'
                                            ).update_traces(
                                                line=dict(width=3, color=futuristic_colors['primary'])
                                            ).update_layout(
                                                margin=dict(l=40, r=40, t=20, b=40),
                                                hovermode='x unified',
                                                paper_bgcolor='rgba(0,0,0,0)',
                                                plot_bgcolor='rgba(15,16,32,0.3)',
                                                font=dict(
                                                    family="Rajdhani, sans-serif",
                                                    color='#ffffff'
                                                ),
                                                xaxis=dict(
                                                    showgrid=False,
                                                    zeroline=False,
                                                    showline=True,
                                                    linecolor='rgba(255, 255, 255, 0.2)'
                                                ),
                                                yaxis=dict(
                                                    showgrid=True,
                                                    gridcolor='rgba(255, 255, 255, 0.1)',
                                                    zeroline=False,
                                                    showline=True,
                                                    linecolor='rgba(255, 255, 255, 0.2)'
                                                )
                                            )
                                        ),
                                        html.Div(
                                            className="chart-description",
                                            children=[
                                                html.P("Daily average AQI values showing the overall trend over 2023. Identifies pollution patterns and helps predict future air quality conditions.")
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            className="chart-row",
                            children=[
                                html.Div(
                                    className="chart-container",
                                    children=[
                                        html.Div(
                                            className="chart-header",
                                            children=[
                                                html.H3("AQI Forecast (Next 24 Hours)", className="chart-title"),
                                                html.Div(
                                                    className="chart-actions",
                                                    children=[
                                                        html.Div(
                                                            className="chart-action refresh",
                                                            title="Refresh Data"
                                                        ),
                                                        html.Div(
                                                            className="chart-action expand",
                                                            title="Expand"
                                                        )
                                                    ]
                                                ),
                                            ]
                                        ),
                                        dcc.Graph(
                                            id='forecast-chart',
                                            className="animated-chart",
                                            figure=px.line(
                                                forecast_data, 
                                                x='Datetime', 
                                                y='Predicted_AQI',
                                                labels={'Predicted_AQI': 'Predicted AQI', 'Datetime': 'Time'},
                                                template='plotly_dark'
                                            ).update_traces(
                                                line=dict(width=3, color=futuristic_colors['accent3'])
                                            ).update_layout(
                                                margin=dict(l=40, r=40, t=20, b=40),
                                                paper_bgcolor='rgba(0,0,0,0)',
                                                plot_bgcolor='rgba(15,16,32,0.3)',
                                                font=dict(
                                                    family="Rajdhani, sans-serif",
                                                    color='#ffffff'
                                                ),
                                                xaxis=dict(
                                                    showgrid=False,
                                                    zeroline=False,
                                                    showline=True,
                                                    linecolor='rgba(255, 255, 255, 0.2)'
                                                ),
                                                yaxis=dict(
                                                    showgrid=True,
                                                    gridcolor='rgba(255, 255, 255, 0.1)',
                                                    zeroline=False,
                                                    showline=True,
                                                    linecolor='rgba(255, 255, 255, 0.2)'
                                                )
                                            )
                                        ),
                                        html.Div(
                                            className="chart-description",
                                            children=[
                                                html.P("Predicted AQI values for the next 24 hours based on historical patterns. Plan your activities accordingly.")
                                            ]
                                        )
                                    ]
                                ),
                                html.Div(
                                    className="chart-container",
                                    children=[
                                        html.Div(
                                            className="chart-header",
                                            children=[
                                                html.H3("Sohna AQI Map", className="chart-title"),
                                                html.Div(
                                                    className="chart-actions",
                                                    children=[
                                                        html.Div(
                                                            className="chart-action refresh",
                                                            title="Refresh Data"
                                                        ),
                                                        html.Div(
                                                            className="chart-action expand",
                                                            title="Expand"
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        dcc.Graph(
                                            id='geospatial-chart',
                                            className="animated-chart",
                                            figure=geo_fig
                                        ),
                                        html.Div(
                                            className="chart-description",
                                            children=[
                                                html.P("Geospatial view of Sohna showing current AQI levels. The color indicates the air quality category.")
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        
                        # Second row - Health Risk and Hourly Pattern
                        html.Div(
                            className="chart-row",
                            children=[
                                html.Div(
                                    className="chart-container",
                                    children=[
                                        html.Div(
                                            className="chart-header",
                                            children=[
                                                html.H3("Health Risk Distribution", className="chart-title"),
                                                html.Div(
                                                    className="chart-actions",
                                                    children=[
                                                        html.Div(
                                                            className="chart-action refresh",
                                                            title="Refresh Data"
                                                        ),
                                                        html.Div(
                                                            className="chart-action expand",
                                                            title="Expand"
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        dcc.Graph(
                                            id='health-risk-chart',
                                            className="animated-chart",
                                            figure=px.pie(
                                                health_risk_counts, 
                                                values='Count', 
                                                names='Health Risk',
                                                color='Health Risk',
                                                color_discrete_map=color_map,
                                                hole=0.6,
                                                template='plotly_dark'
                                            ).update_traces(
                                                textposition='inside',
                                                textinfo='percent+label',
                                                hoverinfo='label+percent+value',
                                                marker=dict(line=dict(color=futuristic_colors['background'], width=2))
                                            ).update_layout(
                                                margin=dict(l=20, r=20, t=20, b=20),
                                                paper_bgcolor='rgba(0,0,0,0)',
                                                plot_bgcolor='rgba(0,0,0,0)',
                                                font=dict(
                                                    family="Rajdhani, sans-serif",
                                                    color='#ffffff'
                                                ),
                                                legend=dict(
                                                    orientation="h",
                                                    yanchor="bottom",
                                                    y=-0.2,
                                                    xanchor="center",
                                                    x=0.5,
                                                    font=dict(
                                                        family="Rajdhani, sans-serif",
                                                        color='#ffffff'
                                                    )
                                                )
                                            )
                                        ),
                                        html.Div(
                                            className="chart-description",
                                            children=[
                                                html.P("Distribution of health risk categories based on AQI measurements in 2023. Shows the proportion of time spent in each air quality category.")
                                            ]
                                        )
                                    ]
                                ),
                                
                                html.Div(
                                    className="chart-container",
                                    children=[
                                        html.Div(
                                            className="chart-header",
                                            children=[
                                                html.H3("Hourly AQI Pattern", className="chart-title"),
                                                html.Div(
                                                    className="chart-actions",
                                                    children=[
                                                        html.Div(
                                                            className="chart-action refresh",
                                                            title="Refresh Data"
                                                        ),
                                                        html.Div(
                                                            className="chart-action expand",
                                                            title="Expand"
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        dcc.Graph(
                                            id='hourly-pattern-chart',
                                            className="animated-chart",
                                            figure=px.bar(
                                                hourly_avg, 
                                                x='Hour_Num', 
                                                y='AQI',
                                                labels={'AQI': 'Average AQI', 'Hour_Num': 'Hour of Day'},
                                                template='plotly_dark'
                                            ).update_traces(
                                                marker_color=futuristic_colors['accent2'],
                                                marker=dict(
                                                    line=dict(width=0),
                                                    opacity=0.8
                                                )
                                            ).update_layout(
                                                margin=dict(l=40, r=40, t=20, b=40),
                                                paper_bgcolor='rgba(0,0,0,0)',
                                                plot_bgcolor='rgba(15,16,32,0.3)',
                                                font=dict(
                                                    family="Rajdhani, sans-serif",
                                                    color='#ffffff'
                                                ),
                                                xaxis=dict(
                                                    tickmode='array',
                                                    tickvals=list(range(0, 24)),
                                                    ticktext=[f"{i}:00" for i in range(0, 24)],
                                                    showgrid=False,
                                                    zeroline=False,
                                                    showline=True,
                                                    linecolor='rgba(255, 255, 255, 0.2)'
                                                ),
                                                yaxis=dict(
                                                    showgrid=True,
                                                    gridcolor='rgba(255, 255, 255, 0.1)',
                                                    zeroline=False,
                                                    showline=True,
                                                    linecolor='rgba(255, 255, 255, 0.2)'
                                                )
                                            )
                                        ),
                                        html.Div(
                                            className="chart-description",
                                            children=[
                                                html.P("Average AQI values by hour of the day, showing daily patterns. Helps identify peak pollution hours for better planning.")
                                            ]
                                        )
                                    ]
                                ),
                            ]
                        ),
                        
                        # Third row - Monthly and Day of Week
                        html.Div(
                            className="chart-row",
                            children=[
                                html.Div(
                                    className="chart-container",
                                    children=[
                                        html.Div(
                                            className="chart-header",
                                            children=[
                                                html.H3("Monthly AQI Pattern (2023)", className="chart-title"),
                                                html.Div(
                                                    className="chart-actions",
                                                    children=[
                                                        html.Div(
                                                            className="chart-action refresh",
                                                            title="Refresh Data"
                                                        ),
                                                        html.Div(
                                                            className="chart-action expand",
                                                            title="Expand"
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        dcc.Graph(
                                            id='monthly-pattern-chart',
                                            className="animated-chart",
                                            figure=px.line(
                                                monthly_avg, 
                                                x='Month_Name', 
                                                y='AQI',
                                                markers=True,
                                                labels={'AQI': 'Average AQI', 'Month_Name': 'Month'},
                                                template='plotly_dark'
                                            ).update_traces(
                                                line=dict(width=3, color=futuristic_colors['accent1']),
                                                marker=dict(size=10, color=futuristic_colors['accent1'])
                                            ).update_layout(
                                                margin=dict(l=40, r=40, t=20, b=40),
                                                paper_bgcolor='rgba(0,0,0,0)',
                                                plot_bgcolor='rgba(15,16,32,0.3)',
                                                font=dict(
                                                    family="Rajdhani, sans-serif",
                                                    color='#ffffff'
                                                ),
                                                xaxis=dict(
                                                    categoryorder='array',
                                                    categoryarray=month_order,
                                                    showgrid=False,
                                                    zeroline=False,
                                                    showline=True,
                                                    linecolor='rgba(255, 255, 255, 0.2)'
                                                ),
                                                yaxis=dict(
                                                    showgrid=True,
                                                    gridcolor='rgba(255, 255, 255, 0.1)',
                                                    zeroline=False,
                                                    showline=True,
                                                    linecolor='rgba(255, 255, 255, 0.2)'
                                                )
                                            )
                                        ),
                                        html.Div(
                                            className="chart-description",
                                            children=[
                                                html.P("Average AQI values by month in 2023, showing seasonal patterns. Reveals how weather and seasonal activities impact air quality.")
                                            ]
                                        )
                                    ]
                                ),
                                
                                html.Div(
                                    className="chart-container",
                                    children=[
                                        html.Div(
                                            className="chart-header",
                                            children=[
                                                html.H3("Day of Week AQI Pattern", className="chart-title"),
                                                html.Div(
                                                    className="chart-actions",
                                                    children=[
                                                        html.Div(
                                                            className="chart-action refresh",
                                                            title="Refresh Data"
                                                        ),
                                                        html.Div(
                                                            className="chart-action expand",
                                                            title="Expand"
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        dcc.Graph(
                                            id='day-of-week-chart',
                                            className="animated-chart",
                                            figure=px.bar(
                                                day_of_week_avg, 
                                                x='Day_of_Week', 
                                                y='AQI',
                                                labels={'AQI': 'Average AQI', 'Day_of_Week': 'Day'},
                                                template='plotly_dark'
                                            ).update_traces(
                                                marker_color=futuristic_colors['secondary'],
                                                marker=dict(
                                                    line=dict(width=0),
                                                    opacity=0.8
                                                )
                                            ).update_layout(
                                                margin=dict(l=40, r=40, t=20, b=40),
                                                paper_bgcolor='rgba(0,0,0,0)',
                                                plot_bgcolor='rgba(15,16,32,0.3)',
                                                font=dict(
                                                    family="Rajdhani, sans-serif",
                                                    color='#ffffff'
                                                ),
                                                xaxis=dict(
                                                    categoryorder='array',
                                                    categoryarray=day_order,
                                                    showgrid=False,
                                                    zeroline=False,
                                                    showline=True,
                                                    linecolor='rgba(255, 255, 255, 0.2)'
                                                ),
                                                yaxis=dict(
                                                    showgrid=True,
                                                    gridcolor='rgba(255, 255, 255, 0.1)',
                                                    zeroline=False,
                                                    showline=True,
                                                    linecolor='rgba(255, 255, 255, 0.2)'
                                                )
                                            )
                                        ),
                                        html.Div(
                                            className="chart-description",
                                            children=[
                                                html.P("Average AQI values by day of the week, showing weekly patterns. Helps identify how human activities affect air quality.")
                                            ]
                                        )
                                    ]
                                ),
                            ]
                        ),
                        
                        # Fourth row - AQI Heatmap
                        html.Div(
                            className="chart-row",
                            children=[
                                html.Div(
                                    className="chart-container large",
                                    children=[
                                        html.Div(
                                            className="chart-header",
                                            children=[
                                                html.H3("AQI Heatmap by Hour and Day", className="chart-title"),
                                                html.Div(
                                                    className="chart-actions",
                                                    children=[
                                                        html.Div(
                                                            className="chart-action refresh",
                                                            title="Refresh Data"
                                                        ),
                                                        html.Div(
                                                            className="chart-action expand",
                                                            title="Expand"
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        dcc.Graph(
                                            id='heatmap-chart',
                                            className="animated-chart",
                                            figure=px.density_heatmap(
                                                df, 
                                                x='Hour_Num', 
                                                y='Day_of_Week',
                                                z='AQI',
                                                histfunc='avg',
                                                labels={'AQI': 'Average AQI', 'Hour_Num': 'Hour of Day', 'Day_of_Week': 'Day of Week'},
                                                color_continuous_scale=[
                                                    [0, '#00e400'],  # Good
                                                    [0.2, '#ffff00'],  # Moderate
                                                    [0.4, '#ff7e00'],  # Unhealthy for Sensitive Groups
                                                    [0.6, '#ff0000'],  # Unhealthy
                                                    [0.8, '#99004c'],  # Very Unhealthy
                                                    [1, '#7e0023']    # Hazardous
                                                ],
                                                template='plotly_dark'
                                            ).update_layout(
                                                margin=dict(l=40, r=40, t=20, b=40),
                                                paper_bgcolor='rgba(0,0,0,0)',
                                                plot_bgcolor='rgba(15,16,32,0.3)',
                                                font=dict(
                                                    family="Rajdhani, sans-serif",
                                                    color='#ffffff'
                                                ),
                                                xaxis=dict(
                                                    tickmode='array',
                                                    tickvals=list(range(0, 24)),
                                                    ticktext=[f"{i}:00" for i in range(0, 24)],
                                                    showgrid=False,
                                                    zeroline=False,
                                                    showline=True,
                                                    linecolor='rgba(255, 255, 255, 0.2)'
                                                ),
                                                yaxis=dict(
                                                    categoryorder='array',
                                                    categoryarray=day_order,
                                                    showgrid=False,
                                                    zeroline=False,
                                                    showline=True,
                                                    linecolor='rgba(255, 255, 255, 0.2)'
                                                ),
                                                coloraxis=dict(
                                                    colorbar=dict(
                                                        title='AQI',
                                                        title_font=dict(
                                                            family="Rajdhani, sans-serif",
                                                            color='#ffffff'
                                                        ),
                                                        tickfont=dict(
                                                            family="Rajdhani, sans-serif",
                                                            color='#ffffff'
                                                        ),
                                                        tickvals=[50, 100, 150, 200, 300, 400],
                                                        ticktext=['Good', 'Moderate', 'Unhealthy for Sensitive', 'Unhealthy', 'Very Unhealthy', 'Hazardous']
                                                    )
                                                )
                                            )
                                        ),
                                        html.Div(
                                            className="chart-description",
                                            children=[
                                                html.P("Heatmap showing average AQI values by hour of day and day of week. Identifies specific time periods with the worst air quality.")
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        
                        # Fifth row - Interactive Explorer
                        html.Div(
                            className="chart-row",
                            children=[
                                html.Div(
                                    className="chart-container large",
                                    children=[
                                        html.Div(
                                            className="chart-header",
                                            children=[
                                                html.H3("Interactive AQI Explorer", className="chart-title"),
                                                html.Div(
                                                    className="chart-actions",
                                                    children=[
                                                        html.Div(
                                                            className="chart-action refresh",
                                                            title="Refresh Data"
                                                        ),
                                                        html.Div(
                                                            className="chart-action expand",
                                                            title="Expand"
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            className="filter-container",
                                            children=[
                                                html.Div(
                                                    className="filter-item",
                                                    children=[
                                                        html.Label("Select View Type:"),
                                                        dcc.RadioItems(
                                                            id='view-type',
                                                            options=[
                                                                {'label': 'Daily', 'value': 'daily'},
                                                                {'label': 'Hourly', 'value': 'hourly'},
                                                                {'label': 'Health Risk', 'value': 'health'}
                                                            ],
                                                            value='daily',
                                                            className="radio-items"
                                                        )
                                                    ]
                                                ),
                                                html.Div(
                                                    className="filter-item",
                                                    children=[
                                                        html.Label("Select Chart Type:"),
                                                        dcc.Dropdown(
                                                            id='chart-type',
                                                            options=[
                                                                {'label': 'Line Chart', 'value': 'line'},
                                                                {'label': 'Bar Chart', 'value': 'bar'},
                                                                {'label': 'Scatter Plot', 'value': 'scatter'}
                                                            ],
                                                            value='line',
                                                            clearable=False,
                                                            className="dropdown"
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        dcc.Graph(
                                            id='interactive-chart',
                                            className="animated-chart"
                                        ),
                                        html.Div(
                                            className="chart-description",
                                            children=[
                                                html.P("Explore AQI data with different views and chart types. Customize your analysis to focus on specific aspects of air quality.")
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        
        # Footer
        html.Div(
            className="footer",
            children=[
                html.Div(
                    className="footer-content",
                    children=[
                        html.Div(
                            className="footer-section",
                            children=[
                                html.H4("About This Dashboard"),
                                html.P("This AQI monitoring dashboard provides comprehensive air quality analysis for Sohna based on 2023 data. It helps users understand pollution patterns, health risks, and make informed decisions based on air quality data.")
                            ]
                        ),
                        html.Div(
                            className="footer-section",
                            children=[
                                html.H4("Dashboard Features"),
                                html.Ul([
                                    html.Li("Historical AQI monitoring"),
                                    html.Li("Health risk assessment"),
                                    html.Li("Temporal pattern analysis"),
                                    html.Li("Interactive data exploration")
                                ])
                            ]
                        ),
                        html.Div(
                            className="footer-section",
                            children=[
                                html.H4("Created For"),
                                html.P("Hackathon 2025"),
                                html.P("Data Source: Sohna AQI Measurements 2023"),
                                html.P("Built with Dash and Plotly")
                            ]
                        )
                    ]
                ),
                html.Div(
                    className="footer-bottom",
                    children=[
                        html.P("© 2025 AERO·PULSE. All rights reserved.")
                    ]
                )
            ]
        ),
        
        # JavaScript for updating the clock
        html.Script("""
            function updateClock() {
                const now = new Date();
                const timeString = now.toLocaleTimeString();
                const dateString = now.toLocaleDateString();
                document.getElementById('live-clock').textContent = dateString + ' ' + timeString;
            }
            
            // Update the clock every second
            setInterval(updateClock, 1000);
            
            // Initial update
            updateClock();
        """)
    ]
)

# Callback for interactive chart
@callback(
    Output('interactive-chart', 'figure'),
    [Input('view-type', 'value'),
     Input('chart-type', 'value')]
)
def update_interactive_chart(view_type, chart_type):
    if view_type == 'daily':
        data_df = daily_avg
        x_col = 'Date'
        title = 'Daily AQI Values'
        color = futuristic_colors['primary']
    elif view_type == 'hourly':
        data_df = hourly_avg
        x_col = 'Hour_Num'
        title = 'Hourly AQI Pattern'
        color = futuristic_colors['accent2']
    else:  # health risk
        # Create a dataframe with average AQI for each health risk category
        data_df = df.groupby('Health Risk')['AQI'].mean().reset_index()
        data_df = data_df.sort_values('AQI')
        x_col = 'Health Risk'
        title = 'Average AQI by Health Risk Category'
        color = None  # Will use color mapping

    # Create the appropriate chart type
    if chart_type == 'line':
        if view_type == 'hourly':
            fig = px.line(
                data_df, 
                x=x_col, 
                y='AQI',
                markers=True,
                labels={'AQI': 'Air Quality Index'},
                title=title,
                template='plotly_dark'
            )
            fig.update_layout(
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(0, 24)),
                    ticktext=[f"{i}:00" for i in range(0, 24)]
                )
            )
        elif view_type == 'health':
            fig = px.bar(
                data_df, 
                x=x_col, 
                y='AQI',
                color=x_col,
                color_discrete_map=color_map,
                labels={'AQI': 'Average AQI'},
                title=title,
                template='plotly_dark'
            )
        else:
            fig = px.line(
                data_df, 
                x=x_col, 
                y='AQI',
                labels={'AQI': 'Air Quality Index', 'Date': 'Date'},
                title=title,
                template='plotly_dark'
            )
    elif chart_type == 'bar':
        if view_type == 'health':
            fig = px.bar(
                data_df, 
                x=x_col, 
                y='AQI',
                color=x_col,
                color_discrete_map=color_map,
                labels={'AQI': 'Average AQI'},
                title=title,
                template='plotly_dark'
            )
        else:
            fig = px.bar(
                data_df, 
                x=x_col, 
                y='AQI',
                labels={'AQI': 'Air Quality Index'},
                title=title,
                template='plotly_dark'
            )
            if view_type == 'hourly':
                fig.update_layout(
                    xaxis=dict(
                        tickmode='array',
                        tickvals=list(range(0, 24)),
                        ticktext=[f"{i}:00" for i in range(0, 24)]
                    )
                )
    else:  # scatter
        if view_type == 'health':
            fig = px.scatter(
                data_df, 
                x=x_col, 
                y='AQI',
                color=x_col,
                color_discrete_map=color_map,
                size='AQI',
                labels={'AQI': 'Average AQI'},
                title=title,
                template='plotly_dark'
            )
        else:
            fig = px.scatter(
                data_df, 
                x=x_col, 
                y='AQI',
                labels={'AQI': 'Air Quality Index'},
                title=title,
                template='plotly_dark'
            )
            if view_type == 'hourly':
                fig.update_layout(
                    xaxis=dict(
                        tickmode='array',
                        tickvals=list(range(0, 24)),
                        ticktext=[f"{i}:00" for i in range(0, 24)]
                    )
                )

    # Common layout updates for dark theme
    fig.update_layout(
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode='closest',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15,16,32,0.3)',
        font=dict(
            family="Rajdhani, sans-serif",
            color='#ffffff'
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='rgba(255, 255, 255, 0.2)'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            zeroline=False,
            showline=True,
            linecolor='rgba(255, 255, 255, 0.2)'
        ),
        title=dict(
            font=dict(
                family="Orbitron, sans-serif",
                color='#ffffff'
            )
        )
    )

    # Update trace colors if not health risk view
    if view_type != 'health' and color is not None:
        fig.update_traces(marker_color=color)
        if chart_type == 'line':
            fig.update_traces(line=dict(width=3, color=color))

    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)