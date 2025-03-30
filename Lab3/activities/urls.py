from django.urls import path
from . import views
from Controllers.workout_history_controller import (
    workout_history_list_controller,
    add_to_history_form_controller,
    add_to_history_controller,
    remove_from_history_controller
)

app_name = 'activities'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_activities, name='search'),
    path('activity/<int:pk>/', views.activity_detail, name='activity_detail'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('profile/', views.profile, name='profile'),
    path('favorites/', views.favorites, name='favorites'),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    # Workout History URLs
    path('workout-history/', workout_history_list_controller, name='workout_history'),
    path('activity/<int:pk>/add-to-history/', add_to_history_form_controller, name='add_to_history_form'),
    path('history/add/', add_to_history_controller, name='add_to_history'),
    path('history/<int:pk>/remove/', remove_from_history_controller, name='remove_from_history'),
    
    path('get-distances/', views.get_distances, name='get_distances'),
] 