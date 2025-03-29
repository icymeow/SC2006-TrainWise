import json
import requests
from datetime import datetime, timedelta
from django.db.models import Avg, Count
from math import radians, sin, cos, sqrt, atan2
from .models import Activity, ActivityHistory, UserPreference, FavoriteActivity

def get_weather_data():
    """Fetch current weather data from data.gov.sg."""
    try:
        url = "https://api.data.gov.sg/v1/environment/24-hour-weather-forecast"
        response = requests.get(url)
        data = response.json()
        
        # Extract relevant weather information
        forecast = data['items'][0]['general']['forecast']
        temperature = data['items'][0]['general']['temperature']
        
        return {
            'forecast': forecast,
            'temperature': temperature
        }
    except Exception as e:
        print(f"Error fetching weather data: {str(e)}")
        return None

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula."""
    R = 6371  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return round(R * c, 1)

def is_bad_weather(weather_data):
    """Determine if weather conditions are unsuitable for outdoor activities."""
    if not weather_data:
        return False
        
    condition = weather_data.get('condition', '').lower()
    temperature = weather_data.get('temp_c', 20)
    aqi = weather_data.get('air_quality', {}).get('pm2_5', 0)
    
    # Bad weather conditions
    bad_conditions = ['rain', 'thunderstorm', 'snow', 'sleet', 'hail']
    is_bad_condition = any(cond in condition for cond in bad_conditions)
    
    # Check temperature and air quality
    is_extreme_temp = temperature > 35 or temperature < 10
    is_bad_air = aqi > 100
    
    return is_bad_condition or is_extreme_temp or is_bad_air

def calculate_distance_score(distance):
    """Calculate score based on distance (0-5 points)."""
    if distance <= 1:
        return 5
    elif distance <= 2:
        return 4
    elif distance <= 3:
        return 3
    elif distance <= 5:
        return 2
    else:
        return 0

def get_activity_score(activity, user_lat, user_lon, user_preferences, weather_data):
    """Calculate a score for an activity based on various factors."""
    score = 0
    
    # Distance score (max 40 points)
    if user_lat and user_lon and activity.latitude and activity.longitude:
        distance = calculate_distance(user_lat, user_lon, activity.latitude, activity.longitude)
        if distance <= user_preferences.max_distance:
            score += max(0, 40 - (distance * 2))  # Decrease score as distance increases
    
    # Weather compatibility score (max 20 points)
    if weather_data:
        weather_forecast = weather_data['forecast'].lower()
        temperature = weather_data['temperature']
        
        # Indoor activities get bonus points during bad weather
        if 'rain' in weather_forecast or 'thunder' in weather_forecast:
            if activity.activity_type in ['GYM', 'YOGA']:  # Indoor activities
                score += 20
            else:
                score -= 10
        
        # Temperature considerations
        if temperature['high'] > 32:  # Hot weather
            if activity.activity_type in ['SWIMMING', 'GYM']:
                score += 10
            elif activity.activity_type in ['RUNNING', 'FOOTBALL']:
                score -= 5
    
    # User preference match score (max 20 points)
    if activity.activity_type in user_preferences.get_preferred_activity_types():
        score += 20
    
    if activity.intensity == user_preferences.preferred_intensity:
        score += 10
    
    # Historical engagement score (max 10 points)
    user_history = ActivityHistory.objects.filter(
        user=user_preferences.user,
        activity__activity_type=activity.activity_type
    )
    
    if user_history.exists():
        avg_rating = user_history.aggregate(Avg('rating'))['rating__avg']
        if avg_rating:
            score += min(10, avg_rating * 2)
    
    return max(0, min(100, score))  # Ensure score is between 0 and 100

def get_recommended_activities(user, user_location, weather_data):
    """
    Get recommended activities based on:
    1. Weather conditions (filter indoor/outdoor appropriately)
    2. Distance from user's location (nearest activities)
    3. User's preferred activity types
    Returns top 3 nearest matching activities.
    """
    print("Starting recommendation process...")  # Debug log
    
    if not user_location or 'latitude' not in user_location or 'longitude' not in user_location:
        print("No user location provided")  # Debug log
        return []

    # Get user preferences
    user_pref = user.userpreference if hasattr(user, 'userpreference') else None
    if not user_pref:
        print("No user preferences found")  # Debug log
        return []

    print(f"User preferences found: {user_pref.get_preferred_activity_types()}")  # Debug log

    # Get all activities first
    activities = Activity.objects.all()
    print(f"Total activities: {activities.count()}")  # Debug log

    # Filter by user's preferred activity types
    if user_pref.preferred_activity_types:
        preferred_types = user_pref.get_preferred_activity_types()
        activities = activities.filter(activity_type__in=preferred_types)
        print(f"Activities after type filter: {activities.count()}")  # Debug log

    # Check weather conditions
    weather_condition = weather_data.get('condition', '').lower()
    is_bad_weather = any(cond in weather_condition for cond in ['rain', 'thunderstorm', 'snow'])
    print(f"Weather condition: {weather_condition}, Is bad weather: {is_bad_weather}")  # Debug log

    if is_bad_weather:
        # If weather is bad, only show indoor activities
        activities = activities.filter(is_indoor=True)
        print(f"Activities after weather filter: {activities.count()}")  # Debug log
    
    # Calculate distances for all matching activities
    activities_with_distance = []
    for activity in activities:
        if activity.latitude and activity.longitude:
            try:
                distance = calculate_distance(
                    user_location['latitude'],
                    user_location['longitude'],
                    float(activity.latitude),
                    float(activity.longitude)
                )
                activities_with_distance.append((activity, distance))
            except (ValueError, TypeError) as e:
                print(f"Error calculating distance for activity {activity.id}: {e}")  # Debug log
                continue

    print(f"Activities with valid distances: {len(activities_with_distance)}")  # Debug log

    # Sort by distance and get top 3 nearest activities
    activities_with_distance.sort(key=lambda x: x[1])  # Sort by distance
    recommended = [activity for activity, _ in activities_with_distance[:3]]
    
    print(f"Final recommended activities: {len(recommended)}")  # Debug log
    for activity in recommended:
        print(f"- {activity.facility_name} ({activity.activity_type})")  # Debug log
    
    return recommended 