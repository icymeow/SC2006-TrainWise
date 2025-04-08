from django.http import JsonResponse
from math import radians, sin, cos, sqrt, atan2
from django.views.decorators.http import require_http_methods
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Activity, ActivityHistory, FavoriteActivity, UserPreference
from .forms import ActivityHistoryForm, UserPreferenceForm
from .services import get_recommended_activities, get_weather_data
import requests
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
import smtplib
import ssl

def get_weather_data():
    """Fetch weather data from wttr.in API"""
    try:
        # Using wttr.in API for Singapore with format=j1 for JSON output
        weather_url = "https://wttr.in/Singapore?format=j1&m"  # Added metric units parameter
        
        headers = {
            'User-Agent': 'Mozilla/5.0',  # Updated User-Agent
            'Accept': 'application/json'
        }
        
        # Fetch weather data with increased timeout
        weather_response = requests.get(weather_url, headers=headers, timeout=10)
        weather_response.raise_for_status()  # Raise exception for bad status codes
        
        try:
            weather_data = weather_response.json()
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON response: {e}")
            print(f"Response content: {weather_response.text[:200]}")  # Print first 200 chars of response
            raise
        
        # Extract current weather information
        if not weather_data.get('current_condition'):
            raise KeyError("No current condition data in response")
            
        current = weather_data['current_condition'][0]
        
        # Get basic weather information with fallbacks
        temperature = current.get('temp_C', 'N/A')
        if temperature != 'N/A':
            temperature = int(float(temperature))
            
        humidity = current.get('humidity', 'N/A')
        if humidity != 'N/A':
            humidity = int(humidity)
            
        # Get weather description
        weather_desc = current.get('weatherDesc', [{}])[0].get('value', 'Unknown')
        
        # Get weather code and ensure it's a string
        weather_code = str(current.get('weatherCode', '113'))  # Default to clear sky if no code
        
        # Map wttr.in weather codes to our icon classes
        icon_mapping = {
            "113": "sun",  # Clear
            "116": "cloud-sun",  # Partly cloudy
            "119": "cloud",  # Cloudy
            "122": "cloud",  # Overcast
            "176": "cloud-rain",  # Light rain
            "179": "cloud-rain",  # Light sleet
            "182": "cloud-rain",  # Light sleet
            "185": "cloud-rain",  # Light sleet
            "200": "cloud-bolt",  # Thundery outbreaks
            "227": "cloud-rain",  # Light snow
            "230": "cloud-rain",  # Heavy snow
            "248": "cloud",  # Fog
            "260": "cloud",  # Freezing fog
            "263": "cloud-rain",  # Light rain
            "266": "cloud-rain",  # Light rain
            "281": "cloud-rain",  # Light sleet
            "284": "cloud-rain",  # Light sleet
            "293": "cloud-rain",  # Light rain
            "296": "cloud-rain",  # Light rain
            "299": "cloud-showers-heavy",  # Heavy rain
            "302": "cloud-showers-heavy",  # Heavy rain
            "305": "cloud-rain",  # Light rain
            "308": "cloud-showers-heavy",  # Heavy rain
            "311": "cloud-rain",  # Light sleet
            "314": "cloud-rain",  # Light sleet
            "317": "cloud-rain",  # Light sleet
            "350": "cloud-rain",  # Light sleet
            "353": "cloud-rain",  # Light rain
            "356": "cloud-showers-heavy",  # Heavy rain
            "359": "cloud-showers-heavy",  # Heavy rain
            "362": "cloud-rain",  # Light sleet
            "365": "cloud-rain",  # Light sleet
            "386": "cloud-bolt",  # Thundery outbreaks
            "389": "cloud-bolt",  # Thundery outbreaks
            "392": "cloud-bolt",  # Thundery snow
            "395": "cloud-bolt"  # Thundery snow
        }
        
        # Get air quality data with fallback
        air_quality = current.get('air_quality', {}).get('us-epa-index', 1)
        try:
            air_quality = int(air_quality)
        except (ValueError, TypeError):
            air_quality = 1  # Default to "Good" if invalid
            
        # Map air quality index to labels
        aqi_labels = {
            1: "Good",
            2: "Moderate",
            3: "Unhealthy for Sensitive Groups",
            4: "Unhealthy",
            5: "Very Unhealthy",
            6: "Hazardous"
        }
        
        return {
            'temperature': temperature,
            'condition': weather_desc,
            'description': weather_desc,
            'humidity': humidity,
            'aqi': air_quality,
            'aqi_label': aqi_labels.get(air_quality, "Unknown"),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'icon': icon_mapping.get(weather_code, 'cloud'),
            'is_day': current.get('isDayTime', '1') == '1',
            'error': None
        }
        
    except requests.RequestException as e:
        print(f"Network error fetching weather data: {e}")
        if hasattr(e, 'response'):
            print(f"Response status code: {e.response.status_code}")
            print(f"Response content: {e.response.text[:200]}")  # Print first 200 chars
            
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        print(f"Error parsing weather data: {e}")
        
    except Exception as e:
        print(f"Unexpected error fetching weather data: {type(e).__name__}: {e}")
        
    # Return default values if any error occurs
    return {
        'error': 'Weather data temporarily unavailable',
        'temperature': 'N/A',
        'condition': 'Data unavailable',
        'description': 'Weather data temporarily unavailable',
        'humidity': 'N/A',
        'aqi': 'N/A',
        'aqi_label': 'N/A',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'icon': 'cloud',
        'is_day': True
    }

def home(request):
    """Home page view showing current weather conditions"""
    weather_info = get_weather_data()
    return render(request, 'activities/home.html', {
        'weather_info': weather_info,
    })

@login_required
@require_http_methods(["GET", "POST"])
def recommendations(request):
    """View for displaying personalized activity recommendations."""
    print("\n=== Starting recommendations view ===")  # Debug log
    
    # Get user preferences
    user_pref = UserPreference.objects.filter(user=request.user).first()
    
    if not user_pref:
        print("No user preferences found, redirecting to profile")  # Debug log
        messages.warning(request, 'Please set your preferences to get personalized recommendations.')
        return redirect('activities:profile')
    
    print(f"User preferences found for user {request.user.username}")  # Debug log
    print(f"Preferred activity types: {user_pref.get_preferred_activity_types()}")  # Debug log
    
    # Get current weather data
    weather_data = get_weather_data()
    print(f"Weather data: {weather_data}")  # Debug log
    
    # Get user's favorite activities
    favorite_activities = []
    if request.user.is_authenticated:
        favorite_activities = FavoriteActivity.objects.filter(user=request.user).values_list('activity', flat=True)
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_location = {
                'latitude': float(data.get('latitude')),
                'longitude': float(data.get('longitude'))
            }
            print(f"Received location data: {user_location}")  # Debug log
            
            # Get recommended activities using new algorithm with real location
            recommended_activities = get_recommended_activities(request.user, user_location, weather_data)
            print(f"Got {len(recommended_activities)} recommended activities")  # Debug log
            
            # Calculate distances for all recommended activities
            distances = []
            for activity, score in recommended_activities:
                if activity.latitude and activity.longitude:
                    try:
                        distance = calculate_distance(
                            user_location['latitude'],
                            user_location['longitude'],
                            float(activity.latitude),
                            float(activity.longitude)
                        )
                        distances.append({
                            'activity_id': activity.id,
                            'distance': round(distance, 1),
                            'score': round(score, 1)
                        })
                    except (ValueError, TypeError) as e:
                        print(f"Error calculating distance for activity {activity.id}: {e}")  # Debug log
                        continue
            
            print(f"Calculated distances for {len(distances)} activities")  # Debug log
            return JsonResponse({'distances': distances})
            
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")  # Debug log
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            print(f"Error processing request: {e}")  # Debug log
            return JsonResponse({'error': str(e)}, status=500)
    
    # For GET requests, use default location (will be updated by JavaScript)
    default_location = {
        'latitude': 1.3521,  # Default to Singapore
        'longitude': 103.8198
    }
    
    # Get initial recommendations with default location
    recommended_activities = get_recommended_activities(request.user, default_location, weather_data)
    print(f"Initial recommendations count: {len(recommended_activities)}")  # Debug log
    
    context = {
        'recommended_activities': recommended_activities,
        'weather_data': weather_data,
        'favorite_activities': favorite_activities,
    }
    
    return render(request, 'activities/recommendations.html', context)

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on Earth using the Haversine formula.
    Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return round(distance, 1)

@require_http_methods(["POST"])
def get_distances(request):
    """Calculate distances between user's location and all activities."""
    try:
        data = json.loads(request.body)
        user_lat = float(data.get('latitude'))
        user_lng = float(data.get('longitude'))
        
        activities = Activity.objects.all()
        distances = {}
        
        for activity in activities:
            if activity.latitude and activity.longitude:
                try:
                    distance = calculate_distance(
                        user_lat, user_lng,
                        float(activity.latitude), float(activity.longitude)
                    )
                    distances[str(activity.id)] = round(distance, 1)
                except (ValueError, TypeError) as e:
                    print(f"Error calculating distance for activity {activity.id}: {e}")
                    distances[str(activity.id)] = None
            else:
                distances[str(activity.id)] = None
        
        return JsonResponse({'distances': distances})
    except (ValueError, json.JSONDecodeError, KeyError) as e:
        print(f"Error in get_distances: {e}")
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def activity_detail(request, pk):
    """Display detailed information about an activity."""
    activity = get_object_or_404(Activity, pk=pk)
    is_favorite = FavoriteActivity.objects.filter(user=request.user, activity=activity).exists()
    history_entries = ActivityHistory.objects.filter(user=request.user, activity=activity).order_by('-date_completed')
    
    context = {
        'activity': activity,
        'is_favorite': is_favorite,
        'history_entries': history_entries,
    }
    
    return render(request, 'activities/activity_detail.html', context)

@login_required
def favorites(request):
    """View for displaying user's favorite activities."""
    print("\n=== Starting favorites view ===")  # Debug log
    print(f"User: {request.user.username}")  # Debug log
    
    favorite_activities = Activity.objects.filter(favoriteactivity__user=request.user)
    print(f"Found {favorite_activities.count()} favorite activities")  # Debug log
    for activity in favorite_activities:
        print(f"- {activity.facility_name}")  # Debug log
    
    return render(request, 'activities/favorites.html', {
        'activities': favorite_activities
    })

@login_required
@require_http_methods(["POST"])
def toggle_favorite(request):
    """Toggle an activity as favorite/unfavorite."""
    print("\n=== Starting toggle_favorite view ===")  # Debug log
    print(f"User: {request.user.username}")  # Debug log
    print(f"Request method: {request.method}")  # Debug log
    print(f"Content type: {request.content_type}")  # Debug log
    
    try:
        data = json.loads(request.body)
        activity_id = data.get('activity_id')
        print(f"Activity ID: {activity_id}")  # Debug log
        
        activity = get_object_or_404(Activity, id=activity_id)
        print(f"Found activity: {activity.facility_name}")  # Debug log
        
        favorite = FavoriteActivity.objects.filter(user=request.user, activity=activity).first()
        print(f"Existing favorite: {favorite}")  # Debug log
        
        if favorite:
            # If it exists, remove it
            favorite.delete()
            is_favorite = False
            print("Removed from favorites")  # Debug log
        else:
            # If it doesn't exist, create it
            FavoriteActivity.objects.create(user=request.user, activity=activity)
            is_favorite = True
            print("Added to favorites")  # Debug log
        
        return JsonResponse({
            'status': 'success',
            'is_favorite': is_favorite,
            'activity_id': activity_id
        })
    except Exception as e:
        print(f"Error in toggle_favorite: {str(e)}")  # Debug log
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def view_workout_history(request):
    """Display user's workout history."""
    history_entries = ActivityHistory.objects.filter(user=request.user).order_by('-date_completed')
    
    context = {
        'history_entries': history_entries,
    }
    
    return render(request, 'activities/workout_history.html', context)

@login_required
def add_to_history_form(request, pk):
    """Display form for adding activity to history."""
    activity = get_object_or_404(Activity, pk=pk)
    
    if request.method == 'POST':
        form = ActivityHistoryForm(request.POST)
        if form.is_valid():
            history_entry = form.save(commit=False)
            history_entry.user = request.user
            history_entry.activity = activity
            history_entry.save()
            return redirect('activities:workout_history')
    else:
        form = ActivityHistoryForm()
    
    context = {
        'activity': activity,
        'form': form,
    }
    
    return render(request, 'activities/add_to_history.html', context)

@login_required
@require_http_methods(["POST"])
def add_to_history(request):
    """Add an activity to user's history."""
    try:
        data = json.loads(request.body)
        activity_id = data.get('activity_id')
        date_completed = data.get('date_completed')
        duration = data.get('duration', {})
        notes = data.get('notes')
        rating = data.get('rating')
        
        if not activity_id or not date_completed:
            return JsonResponse({
                'success': False,
                'error': 'Activity ID and date are required'
            }, status=400)
        
        activity = Activity.objects.get(id=activity_id)
        
        # Convert duration to timedelta
        duration_timedelta = timedelta(
            hours=duration.get('hours', 0),
            minutes=duration.get('minutes', 0)
        )
        
        # Create history entry
        history_entry = ActivityHistory.objects.create(
            user=request.user,
            activity=activity,
            date_completed=date_completed,
            duration=duration_timedelta,
            notes=notes,
            rating=rating
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Activity added to history'
        })
    except Activity.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Activity not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error adding to history: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["POST"])
def remove_from_history(request, pk):
    """Remove an activity from user's history."""
    try:
        history_entry = get_object_or_404(ActivityHistory, pk=pk, user=request.user)
        history_entry.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Activity removed from history'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error removing from history: {str(e)}'
        }, status=500)

def search_activities(request):
    """Search and filter activities."""
    # Get search parameters
    activity_type = request.GET.get('activity_type', '')
    location_type = request.GET.get('location_type', '')
    search_query = request.GET.get('query', '')
    
    # Start with all activities
    activities = Activity.objects.all()
    
    # Apply activity type filter
    if activity_type:
        activities = activities.filter(
            Q(activity_type=activity_type) |
            Q(description__icontains=activity_type.title())  # Convert RUNNING to Running
        )
    
    # Apply indoor/outdoor filter
    if location_type:
        is_indoor = location_type == 'indoor'
        activities = activities.filter(is_indoor=is_indoor)
    
    # Apply search query filter
    if search_query:
        activities = activities.filter(
            Q(facility_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Get user's favorite activities if logged in
    favorite_activities = []
    if request.user.is_authenticated:
        favorite_activities = FavoriteActivity.objects.filter(user=request.user).values_list('activity', flat=True)
    
    context = {
        'activities': activities,
        'activity_types': Activity.ACTIVITY_TYPES,
        'selected_type': activity_type,
        'selected_location': location_type,
        'search_query': search_query,
        'favorite_activities': favorite_activities,
    }
    
    return render(request, 'activities/search.html', context)

@login_required
def update_preferences(request):
    """Update user preferences."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            preferences, created = UserPreference.objects.get_or_create(user=request.user)
            
            if 'preferred_intensity' in data:
                preferences.preferred_intensity = data['preferred_intensity']
            
            if 'preferred_activity_types' in data:
                preferences.set_preferred_activity_types(data['preferred_activity_types'])
            
            if 'max_distance' in data:
                preferences.max_distance = int(data['max_distance'])
            
            if 'indoor_preference' in data:
                preferences.indoor_preference = bool(data['indoor_preference'])
            
            preferences.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Preferences updated successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error updating preferences: {str(e)}'
            }, status=500)
    
    # GET request - return current preferences
    try:
        preferences = UserPreference.objects.get(user=request.user)
        return JsonResponse({
            'preferred_intensity': preferences.preferred_intensity,
            'preferred_activity_types': preferences.get_preferred_activity_types(),
            'max_distance': preferences.max_distance,
            'indoor_preference': preferences.indoor_preference
        })
    except UserPreference.DoesNotExist:
        return JsonResponse({
            'error': 'No preferences found'
        }, status=404)

@login_required
def profile(request):
    """View for displaying and updating user profile."""
    user_pref = UserPreference.objects.get_or_create(user=request.user)[0]

    if request.method == 'POST':
        print(f"POST data received: {request.POST}")  # Debug log
        form = UserPreferenceForm(request.POST, instance=user_pref)
        if form.is_valid():
            print(f"Form is valid. Cleaned data: {form.cleaned_data}")  # Debug log
            
            # Get the activities before saving
            activities = form.cleaned_data.get('preferred_activity_types', [])
            if not activities:
                print("No activities selected")  # Debug log
            else:
                print(f"Selected activities: {activities}")  # Debug log
            
            # Save the form but don't commit yet
            user_pref = form.save(commit=False)
            
            # Explicitly set the activities
            if activities:
                user_pref.preferred_activity_types = ','.join(activities)
            else:
                user_pref.preferred_activity_types = ''
            
            # Now save
            user_pref.save()
            print(f"Saved preferences. Raw value: {user_pref.preferred_activity_types}")  # Debug log
            print(f"Get method returns: {user_pref.get_preferred_activity_types()}")  # Debug log
            
            messages.success(request, 'Your preferences have been updated!')
            return redirect('activities:profile')
        else:
            print(f"Form errors: {form.errors}")  # Debug log
            messages.error(request, 'Please correct the errors below.')
    else:
        # For GET requests, initialize form with current preferences
        initial_data = {}
        if user_pref.preferred_activity_types:
            initial_data['preferred_activity_types'] = user_pref.get_preferred_activity_types()
        form = UserPreferenceForm(instance=user_pref, initial=initial_data)

    return render(request, 'activities/profile.html', {'form': form})

@login_required
def workout_history(request, activity_id):
    """View for displaying and managing workout history."""
    activity = get_object_or_404(Activity, id=activity_id)
    history = ActivityHistory.objects.filter(user=request.user, activity=activity).order_by('-date_completed')
    
    if request.method == 'POST':
        form = ActivityHistoryForm(request.POST)
        if form.is_valid():
            history_entry = form.save(commit=False)
            history_entry.user = request.user
            history_entry.activity = activity
            history_entry.save()
            messages.success(request, 'Workout recorded successfully!')
            return redirect('activities:activity_detail', pk=activity_id)
    else:
        form = ActivityHistoryForm()
    
    return render(request, 'activities/workout_history.html', {
        'activity': activity,
        'history': history,
        'form': form
    })

@login_required
def workout_history_list(request):
    """Display a list of all workout history entries for the user."""
    history_entries = ActivityHistory.objects.filter(user=request.user).order_by('-date_completed')
    activities = Activity.objects.filter(activityhistory__user=request.user).distinct()
    
    context = {
        'history_entries': history_entries,
        'activities': activities,
    }
    return render(request, 'activities/workout_history.html', context)

def test_email(request):
    """Test view to verify email configuration with detailed error handling"""
    try:
        # First test SMTP connection
        smtp_server = settings.EMAIL_HOST
        port = settings.EMAIL_PORT
        sender_email = settings.EMAIL_HOST_USER
        password = settings.EMAIL_HOST_PASSWORD

        # Create a secure SSL/TLS connection
        context = ssl.create_default_context()

        # Try to log in to server and send email
        try:
            server = smtplib.SMTP(smtp_server, port)
            server.ehlo()  # Can be omitted
            server.starttls(context=context)  # Secure the connection
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            print("SMTP connection successful!")
            server.quit()

            # If SMTP connection works, try sending email through Django
            send_mail(
                'Test Email from TrainWise',
                'This is a test email to verify your email configuration is working correctly.',
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],  # Sending to yourself for testing
                fail_silently=False,
            )
            return HttpResponse(
                'SMTP connection test successful! Email sent successfully! '
                f'Check your inbox at {settings.EMAIL_HOST_USER}. '
                'Note: The email might take a few minutes to arrive.'
            )
        except smtplib.SMTPAuthenticationError as e:
            return HttpResponse(
                f'SMTP Authentication failed. This usually means your email or app password is incorrect.<br><br>'
                f'Error details: {str(e)}<br><br>'
                f'Current email: {settings.EMAIL_HOST_USER}<br>'
                'Please verify your app password is correct.'
            )
        except smtplib.SMTPException as e:
            return HttpResponse(f'SMTP error occurred: {str(e)}')
    except Exception as e:
        return HttpResponse(f'General error occurred: {str(e)}') 