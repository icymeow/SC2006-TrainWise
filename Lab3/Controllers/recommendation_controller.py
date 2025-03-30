from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..Database.favorite_activities_database import FavoriteActivitiesDatabase
from ..Database.activity_database import ActivityDatabase

@login_required
def favorite_activities_controller(request):
    favorites = FavoriteActivitiesDatabase.objects.filter(user=request.user)
    return render(request, 'UI/templates/recommendations/favorites.html', {'favorites': favorites})

@login_required
def recommended_activities_controller(request):
    # Get user preferences
    user_preferences = request.user.preferences or {}
    
    # Filter activities based on user preferences
    activities = ActivityDatabase.objects.all()
    
    # Apply filters based on user preferences
    if 'intensity' in user_preferences:
        activities = activities.filter(intensity_level=user_preferences['intensity'])
    if 'activity_type' in user_preferences:
        activities = activities.filter(activity_type=user_preferences['activity_type'])
    
    return render(request, 'UI/templates/recommendations/recommended.html', {'activities': activities}) 