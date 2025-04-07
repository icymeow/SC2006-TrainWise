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
from ..Database.workout_history_database import WorkoutHistory
from .weather_controller import WeatherController
import math
from django.conf import settings

def activity_list_controller(request):
    activities = ActivityDatabase.objects.all()
    return render(request, 'UI/templates/activities/activity_list.html', {'activities': activities})

def activity_detail_controller(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    is_favorite = False
    history_entries = None

    if request.user.is_authenticated:
        is_favorite = FavoriteActivitiesDatabase.objects.filter(user=request.user, activity=activity).exists()
        history_entries = WorkoutHistory.objects.filter(user=request.user, activity=activity).order_by('-date')[:4]

    # Get current weather data for the activity location
    current_weather = WeatherController.get_current_weather(
        latitude=activity.latitude,
        longitude=activity.longitude
    )

    # Check if weather is suitable for outdoor activities
    is_weather_suitable = None
    if not activity.is_indoor:
        is_weather_suitable = WeatherController.is_outdoor_weather_suitable(current_weather)

    context = {
        'activity': activity,
        'is_favorite': is_favorite,
        'history_entries': history_entries,
        'current_weather': current_weather,
        'is_weather_suitable': is_weather_suitable,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, 'UI/templates/activities/activity_detail.html', context)

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
    return render(request, 'UI/templates/activities/search.html', context)

@login_required
def get_activity_recommendations(request):
    """Get personalized activity recommendations based on weather, favorites, history, and distance."""
    
    # Get current weather data
    current_weather = WeatherController.get_current_weather()
    
    # Get all activities
    activities = Activity.objects.all()
    
    # Step 1: Filter based on weather
    if current_weather and (
        current_weather['condition'] == 'rainy' or 
        not WeatherController.is_outdoor_weather_suitable(current_weather)
    ):
        # If rainy or unsuitable weather, only show indoor activities
        activities = activities.filter(is_indoor=True)
    
    # Get user's location (from form or stored preferences)
    user_lat = request.GET.get('latitude')
    user_lng = request.GET.get('longitude')
    
    # Get user's favorite activities
    user_favorites = FavoriteActivitiesDatabase.objects.filter(user=request.user).values_list('activity_id', flat=True)
    
    # Get user's activity history
    user_history = WorkoutHistory.objects.filter(user=request.user)
    activity_frequency = {}
    for history in user_history:
        activity_frequency[history.activity_id] = activity_frequency.get(history.activity_id, 0) + 1
    
    # Calculate priority scores
    activity_scores = []
    for activity in activities:
        score = 0
        
        # Add points for favorites
        if activity.id in user_favorites:
            score += 3
        
        # Adjust score based on frequency
        frequency = activity_frequency.get(activity.id, 0)
        if frequency > 2:
            score -= 2
        
        # Add points based on weather suitability
        if not activity.is_indoor and current_weather:
            if WeatherController.is_outdoor_weather_suitable(current_weather):
                score += 2
            else:
                score -= 1
        
        # Add distance-based score if location available
        if user_lat and user_lng:
            distance = calculate_distance(
                float(user_lat), float(user_lng),
                float(activity.latitude), float(activity.longitude)
            )
            # Add 0-5 points based on distance (closer = more points)
            distance_score = max(0, 5 - (distance / 2))  # 2km = -1 point
            score += distance_score
        
        activity_scores.append((activity, score))
    
    # Sort activities by score
    sorted_activities = [a[0] for a in sorted(activity_scores, key=lambda x: x[1], reverse=True)]
    
    return render(request, 'UI/templates/activities/recommendations.html', {
        'activities': sorted_activities[:10],  # Top 10 recommendations
        'current_weather': current_weather
    }) 