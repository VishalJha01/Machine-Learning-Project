import pandas as pd
import numpy as np

def create_forecast_model(df):
    """Simple test function"""
    print("Creating forecast model...")
    # Return dummy values for testing
    model = "dummy_model"
    scaler = "dummy_scaler"
    features = ["dummy_feature"]
    return model, scaler, features

def predict_next_hours(df, model, scaler, features, hours=24):
    """Simple test function"""
    print(f"Predicting AQI for next {hours} hours...")
    # Return dummy forecast data
    dates = pd.date_range(start=pd.Timestamp.now(), periods=hours, freq='H')
    forecast_data = pd.DataFrame({
        'Datetime': dates,
        'Predicted_AQI': np.random.randint(50, 200, size=hours)
    })
    return forecast_data