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
    1. Weather conditions (primary filter)
    2. Distance from user's location (major factor)
    3. User's preferred activity types
    Returns list of (activity, score) tuples.
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

    # Get preferred types for scoring
    preferred_types = []
    if user_pref.preferred_activity_types:
        preferred_types = [pt.strip("[]'\"").strip().lower() for pt in user_pref.get_preferred_activity_types() if pt.strip("[]'\"").strip()]
        print(f"User preferred activities: {preferred_types}")  # Debug log

    # Enhanced weather condition check
    weather_condition = weather_data.get('condition', '').lower()
    temperature = weather_data.get('temperature', 25)  # Default to 25°C if not provided
    humidity = weather_data.get('humidity', 70)  # Default to 70% if not provided
    
    # Define weather conditions
    is_rainy = any(cond in weather_condition for cond in ['rain', 'thunderstorm', 'drizzle'])
    is_hot = temperature > 32
    is_very_hot = temperature > 35
    is_humid = humidity > 80
    print(f"Weather analysis - Rainy: {is_rainy}, Hot: {is_hot}, Very Hot: {is_very_hot}, Humid: {is_humid}")  # Debug log

    # Calculate scores and distances for all activities
    activities_with_scores = []
    for activity in activities:
        if activity.latitude and activity.longitude:
            try:
                # Calculate base score
                score = 0
                
                # Activity type matching score (max 40 points) - increased weight for matching
                activity_list = [act.strip().lower() for act in activity.description.split('/')]
                matching_activities = 0
                
                # Check for exact matches first
                for pref in preferred_types:
                    for act in activity_list:
                        if pref == act or pref in act:
                            matching_activities += 1
                            break
                
                # If no exact matches, check for partial matches
                if matching_activities == 0:
                    for pref in preferred_types:
                        for act in activity_list:
                            if pref in act or act in pref:
                                matching_activities += 0.5  # Partial match gets half points
                                break
                
                # Calculate preference score (increased to 40 points max)
                preference_score = 40 * (matching_activities / max(len(preferred_types), 1))
                score += preference_score
                
                # Distance score (max 30 points) - more gradual decrease
                distance = calculate_distance(
                    user_location['latitude'],
                    user_location['longitude'],
                    float(activity.latitude),
                    float(activity.longitude)
                )
                
                if distance <= float(user_pref.max_distance):
                    # More gradual distance scoring
                    if distance <= 2:
                        score += 30  # Full points for close activities
                    elif distance <= 5:
                        score += 25 - ((distance - 2) * 2)  # Gradual decrease
                    elif distance <= 10:
                        score += 20 - ((distance - 5))  # Slower decrease
                    elif distance <= 20:
                        score += 15 - ((distance - 10) * 0.5)  # Very gradual decrease
                    else:
                        score += max(0, 10 - ((distance - 20) * 0.2))  # Minimal decrease for far activities
                
                # Weather compatibility score (max 30 points) - balanced importance
                weather_score = 0
                
                # Basic indoor/outdoor scoring
                if activity.is_indoor:
                    if is_rainy:
                        weather_score += 30  # Maximum points for indoor activities during rain
                    elif is_very_hot:
                        weather_score += 25  # High points for indoor during very hot weather
                    elif is_hot:
                        weather_score += 20  # Good points for indoor during hot weather
                    else:
                        weather_score += 15  # Base points for indoor activities
                else:  # Outdoor activities
                    if is_rainy:
                        weather_score -= 5  # Small penalty for outdoor activities in rain
                    elif is_very_hot:
                        weather_score -= 2  # Tiny penalty for outdoor in very hot weather
                    elif is_hot and is_humid:
                        weather_score += 15  # Moderate score for hot and humid conditions
                    else:
                        weather_score += 25  # Good score for outdoor in nice weather
                
                # Activity-specific weather adjustments
                if 'swimming' in str(activity.description).lower():
                    if is_hot or is_very_hot:
                        weather_score += 5  # Bonus for swimming in hot weather
                elif 'gym' in str(activity.description).lower():
                    if is_rainy or is_very_hot:
                        weather_score += 5  # Small bonus for gym in bad weather
                
                score += min(30, weather_score)  # Cap weather score at 30 points
                
                # Only include activities with a minimum score
                if score > 25:  # Lowered minimum threshold
                    activities_with_scores.append((activity, score))
                    print(f"Scored {activity.facility_name}: {score} (Weather: {weather_score}, Distance: {distance}km) - Activities: {activity_list}")  # Debug log
                
            except (ValueError, TypeError) as e:
                print(f"Error calculating score for activity {activity.id}: {e}")  # Debug log
                continue

    print(f"Activities with valid scores: {len(activities_with_scores)}")  # Debug log

    # Sort by score (highest first) and get top recommendations
    activities_with_scores.sort(key=lambda x: x[1], reverse=True)
    recommended = activities_with_scores[:5]  # Get top 5 recommendations
    
    print(f"Final recommended activities: {len(recommended)}")  # Debug log
    for activity, score in recommended:
        print(f"- {activity.facility_name} ({activity.description}): {score}")  # Debug log
    
    return recommended 