from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..Database.favorite_activities_database import FavoriteActivitiesDatabase
from ..activities.models import Activity, UserPreference

@login_required
def favorite_activities_controller(request):
    favorites = FavoriteActivitiesDatabase.objects.filter(user=request.user)
    return render(request, 'UI/templates/recommendations/favorites.html', {'favorites': favorites})

@login_required
def recommended_activities_controller(request):
    # Get user preferences
    try:
        user_preferences = UserPreference.objects.get(user=request.user)
        print(f"Found preferences for user {request.user.username}")
        print(f"Raw preferred types: {user_preferences.preferred_activity_types}")
    except UserPreference.DoesNotExist:
        print(f"No preferences found for user {request.user.username}")
        # If no preferences set, return all activities
        activities = Activity.objects.all()
        return render(request, 'UI/templates/recommendations/recommended.html', {
            'activities': activities,
            'message': 'Set your preferences to get personalized recommendations!'
        })
    
    # Start with all activities
    activities = Activity.objects.all()
    print(f"Total activities: {activities.count()}")
    
    # Get preferred types and convert to uppercase to match Activity model
    preferred_types = [ptype.upper() for ptype in user_preferences.get_preferred_activity_types()]
    print(f"Preferred types (uppercase): {preferred_types}")
    
    # Filter by preferred activity types
    if preferred_types:
        activities = activities.filter(activity_type__in=preferred_types)
        print(f"Activities after type filter: {activities.count()}")
    
    # Filter by indoor/outdoor preference
    if user_preferences.indoor_preference:
        activities = activities.filter(is_indoor=True)
        print(f"Activities after indoor filter: {activities.count()}")
    
    # Sort activities by relevance
    activities = sorted(
        activities,
        key=lambda x: (
            # Higher score for exact activity type matches
            1 if x.activity_type in preferred_types else 0,
            # Higher score for activities within max distance
            1 if not hasattr(x, 'distance') or x.distance <= user_preferences.max_distance else 0,
        ),
        reverse=True
    )
    print(f"Final activities count: {len(activities)}")
    
    return render(request, 'UI/templates/recommendations/recommended.html', {
        'activities': activities,
        'preferences': user_preferences
    }) 