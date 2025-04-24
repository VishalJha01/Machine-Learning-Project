def get_health_recommendations(aqi):
    """
    Get health recommendations based on the current AQI value
    
    Parameters:
    aqi (float): Current Air Quality Index value
    
    Returns:
    dict: Dictionary containing health recommendations
    """
    
    if aqi <= 50:
        return {
            "icon": "✅",
            "general": "Air quality is good. Enjoy outdoor activities.",
            "sensitive_groups": "No special precautions needed.",
            "outdoor_activity": "All outdoor activities are safe.",
            "ventilation": "Open windows to get fresh air.",
            "mask_recommendation": "No masks needed for air quality reasons."
        }
    
    elif aqi <= 100:
        return {
            "icon": "🟢",
            "general": "Air quality is acceptable but may be a concern for those sensitive to air pollution.",
            "sensitive_groups": "Unusually sensitive people should consider reducing prolonged outdoor exertion.",
            "outdoor_activity": "Most outdoor activities are safe.",
            "ventilation": "Open windows to get fresh air.",
            "mask_recommendation": "Generally not needed, but sensitive individuals may consider basic masks."
        }
    
    elif aqi <= 150:
        return {
            "icon": "🟡",
            "general": "Members of sensitive groups may experience health effects.",
            "sensitive_groups": "People with respiratory or heart disease, the elderly and children should limit prolonged outdoor exertion.",
            "outdoor_activity": "Consider reducing or rescheduling strenuous outdoor activities.",
            "ventilation": "Consider keeping windows closed during peak pollution hours.",
            "mask_recommendation": "N95 or KN95 masks recommended for sensitive groups when outdoors."
        }
    
    elif aqi <= 200:
        return {
            "icon": "🟠",
            "general": "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects.",
            "sensitive_groups": "People with respiratory or heart disease, the elderly and children should avoid prolonged outdoor exertion.",
            "outdoor_activity": "Reduce or reschedule strenuous outdoor activities for everyone.",
            "ventilation": "Keep windows closed and use air purifiers if available.",
            "mask_recommendation": "N95 or KN95 masks recommended for everyone when outdoors."
        }
    
    elif aqi <= 300:
        return {
            "icon": "🔴",
            "general": "Health alert: everyone may experience more serious health effects.",
            "sensitive_groups": "People with respiratory or heart disease, the elderly and children should avoid all outdoor activity.",
            "outdoor_activity": "Avoid all outdoor physical activity.",
            "ventilation": "Keep windows closed, use air purifiers, and minimize indoor activities that can cause pollution.",
            "mask_recommendation": "N95 or KN95 masks essential when outdoors, even for short periods."
        }
    
    else:
        return {
            "icon": "⚠️",
            "general": "Health warning of emergency conditions: everyone is more likely to be affected.",
            "sensitive_groups": "Everyone should avoid all outdoor activity.",
            "outdoor_activity": "Avoid all outdoor physical activity and stay indoors.",
            "ventilation": "Keep windows closed, use air purifiers, and avoid activities that can cause indoor pollution.",
            "mask_recommendation": "N95 or KN95 masks essential when outdoors, even for short periods. Consider double masking."
        }