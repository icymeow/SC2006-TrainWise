from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ..Database.activity_database import ActivityDatabase
from ..Database.favorite_activities_database import FavoriteActivitiesDatabase
from django.db.models import Q
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from ..UI.forms.activity_forms import ActivitySearchForm
from ..Database.activity_database import Activity
from ..Database.user_database import UserDatabase
import math
from django.conf import settings
from ..Database.workout_history_database import WorkoutHistory

def activity_list_controller(request):
    activities = ActivityDatabase.objects.all()
    return render(request, 'activities/activity_list.html', {'activities': activities})

def activity_detail_controller(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    is_favorite = False
    history_entries = None

    if request.user.is_authenticated:
        is_favorite = FavoriteActivitiesDatabase.objects.filter(user=request.user, activity=activity).exists()
        history_entries = WorkoutHistory.objects.filter(user=request.user, activity=activity).order_by('-date')[:4]

    # Get current weather data for the activity location
    current_weather = get_current_weather(activity.latitude, activity.longitude)

    context = {
        'activity': activity,
        'is_favorite': is_favorite,
        'history_entries': history_entries,
        'current_weather': current_weather,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, 'activities/activity_detail.html', context)

@login_required
def toggle_favorite_controller(request, pk):
    activity = get_object_or_404(ActivityDatabase, pk=pk)
    favorite, created = FavoriteActivitiesDatabase.objects.get_or_create(user=request.user, activity=activity)
    if not created:
        favorite.delete()
    return JsonResponse({'is_favorite': created})

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    
    return distance

@login_required
def search_activities(request):
    form = ActivitySearchForm(request.GET or None)
    activities = Activity.objects.all()
    
    if form.is_valid():
        # Get search query
        search_query = form.cleaned_data.get('search_query')
        if search_query:
            activities = activities.filter(
                Q(facility_name__icontains=search_query) |
                Q(activities__icontains=search_query)
            )
        
        # Apply filters
        activity_types = form.cleaned_data.get('activity_types')
        if activity_types:
            activities = activities.filter(activity_type__in=activity_types)
        
        intensity_levels = form.cleaned_data.get('intensity_levels')
        if intensity_levels:
            activities = activities.filter(intensity__in=intensity_levels)
        
        weather_conditions = form.cleaned_data.get('weather_conditions')
        if weather_conditions:
            activities = activities.filter(weather_conditions__in=weather_conditions)
        
        # Air quality range
        air_quality_min = form.cleaned_data.get('air_quality_min')
        air_quality_max = form.cleaned_data.get('air_quality_max')
        if air_quality_min:
            activities = activities.filter(air_quality__gte=air_quality_min)
        if air_quality_max:
            activities = activities.filter(air_quality__lte=air_quality_max)
        
        # Location-based filtering
        latitude = form.cleaned_data.get('latitude')
        longitude = form.cleaned_data.get('longitude')
        radius = form.cleaned_data.get('radius')
        
        if latitude and longitude and radius:
            # Filter activities within radius
            filtered_activities = []
            for activity in activities:
                distance = calculate_distance(
                    latitude, longitude,
                    activity.latitude, activity.longitude
                )
                if distance <= radius:
                    filtered_activities.append(activity)
            activities = filtered_activities
        
        # Sorting
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by == 'distance' and latitude and longitude:
            # Sort by distance from user's location
            activities = sorted(
                activities,
                key=lambda x: calculate_distance(
                    latitude, longitude,
                    x.latitude, x.longitude
                )
            )
        elif sort_by == 'popularity':
            activities = activities.order_by('-popularity')
        elif sort_by == 'recommended':
            # Get user preferences
            user = request.user
            user_preferences = UserDatabase.objects.get(id=user.id)
            
            # Sort based on user's favorite sports and preferences
            activities = sorted(
                activities,
                key=lambda x: (
                    # Higher score for matching user's favorite sports
                    sum(1 for sport in user_preferences.favorite_sports 
                        if sport in x.activities.lower()),
                    # Higher score for matching preferred intensity
                    (1 if x.intensity == user_preferences.preferred_intensity else 0),
                    # Higher score for matching preferred weather
                    (1 if x.weather_conditions == user_preferences.preferred_weather else 0),
                    # Higher score for better air quality
                    (500 - x.air_quality) / 500
                ),
                reverse=True
            )
    
    context = {
        'form': form,
        'activities': activities,
    }
    return render(request, 'activities/search.html', context)

@login_required
def get_activity_recommendations(request):
    """Get personalized activity recommendations based on weather, favorites, history, and distance."""
    
    # Get current weather data (assuming we have this from weather API)
    current_weather = get_current_weather()  # You'll need to implement this
    
    # Get all activities
    activities = Activity.objects.all()
    
    # Step 1: Filter based on weather
    if current_weather.get('condition') == 'rainy' or current_weather.get('air_quality') > 100:
        # If rainy or bad air quality, only show indoor activities
        activities = activities.filter(activity_type='indoor')
    
    # Get user's location (from form or stored preferences)
    user_lat = request.GET.get('latitude')
    user_lng = request.GET.get('longitude')
    
    # Get user's favorite activities
    user_favorites = FavoriteActivitiesDatabase.objects.filter(user=request.user).values_list('activity_id', flat=True)
    
    # Get user's activity history (you'll need to implement this model)
    user_history = ActivityHistory.objects.filter(user=request.user)
    activity_frequency = {}
    for history in user_history:
        activity_frequency[history.activity_id] = activity_frequency.get(history.activity_id, 0) + 1
    
    # Step 2: Calculate priority scores
    activity_scores = []
    for activity in activities:
        score = 0
        
        # Add 3 points if in favorites
        if activity.id in user_favorites:
            score += 3
        
        # Subtract 2 points if done frequently
        frequency = activity_frequency.get(activity.id, 0)
        if frequency > 2:  # Consider "frequent" if done more than twice
            score -= 2
        
        # Add 0-5 points based on distance
        if user_lat and user_lng:
            distance = calculate_distance(
                float(user_lat), float(user_lng),
                float(activity.latitude), float(activity.longitude)
            )
            # Score based on distance: 5 points for ≤1km, decreasing to 0 points at 4km
            if distance <= 1:
                distance_score = 5
            elif distance >= 4:
                distance_score = 0
            else:
                distance_score = 5 - ((distance - 1) * (5/3))  # Linear decrease from 5 to 0 between 1km and 4km
            score += distance_score
        
        activity_scores.append((activity, score))
    
    # Step 3: Sort by priority score and get top 3
    recommended_activities = sorted(activity_scores, key=lambda x: x[1], reverse=True)[:3]
    
    context = {
        'current_weather': current_weather,
        'recommended_activities': recommended_activities,
        'user_location': {'latitude': user_lat, 'longitude': user_lng} if user_lat and user_lng else None,
    }
    
    return render(request, 'activities/recommendations.html', context)

def get_current_weather(latitude, longitude):
    """
    Fetch current weather data for the given coordinates using the wttr.in API.
    Returns a dictionary with weather information or None if the data cannot be retrieved.
    """
    try:
        import requests
        import json
        from datetime import datetime
        
        # Using wttr.in API with format=j1 for JSON output
        weather_url = f"https://wttr.in/{latitude},{longitude}?format=j1&m"  # Added metric units parameter
        
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        }
        
        # Fetch weather data with increased timeout
        weather_response = requests.get(weather_url, headers=headers, timeout=10)
        weather_response.raise_for_status()
        
        try:
            weather_data = weather_response.json()
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON response: {e}")
            print(f"Response content: {weather_response.text[:200]}")
            return None
        
        # Extract current weather information
        if not weather_data.get('current_condition'):
            return None
            
        current = weather_data['current_condition'][0]
        
        # Get basic weather information with fallbacks
        temperature = current.get('temp_C', 'N/A')
        if temperature != 'N/A':
            temperature = int(float(temperature))
            
        # Get weather description
        weather_desc = current.get('weatherDesc', [{}])[0].get('value', 'Unknown')
        
        # Get air quality data with fallback
        air_quality = current.get('air_quality', {}).get('us-epa-index', 1)
        try:
            air_quality = int(air_quality)
        except (ValueError, TypeError):
            air_quality = 1  # Default to "Good" if invalid
            
        # Map weather description to our condition format
        weather_mapping = {
            'Clear': 'sunny',
            'Sunny': 'sunny',
            'Partly cloudy': 'cloudy',
            'Cloudy': 'cloudy',
            'Overcast': 'cloudy',
            'Rain': 'rainy',
            'Light rain': 'rainy',
            'Moderate rain': 'rainy',
            'Heavy rain': 'rainy',
            'Thunderstorm': 'rainy',
            'Mist': 'cloudy',
            'Fog': 'cloudy'
        }
        
        # Map the weather description to our condition format
        condition = 'cloudy'  # default
        for key, value in weather_mapping.items():
            if key.lower() in weather_desc.lower():
                condition = value
                break
        
        return {
            'temperature': temperature,
            'condition': condition,
            'air_quality': air_quality,
            'description': weather_desc,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except requests.RequestException as e:
        print(f"Network error fetching weather data: {e}")
        if hasattr(e, 'response'):
            print(f"Response status code: {e.response.status_code}")
            print(f"Response content: {e.response.text[:200]}")
        return None
        
    except Exception as e:
        print(f"Unexpected error fetching weather data: {type(e).__name__}: {e}")
        return None 