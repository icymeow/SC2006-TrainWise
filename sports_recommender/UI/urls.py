from django.urls import path
from . import views

urlpatterns = [
    # ... existing code ...
    
    # Workout History URLs
    path('workout-history/', views.view_workout_history, name='workout_history'),
    path('activities/<int:pk>/add-to-history/', views.add_to_history_form, name='add_to_history_form'),
    path('activities/history/add/', views.add_to_history, name='add_to_history'),
    path('activities/history/<int:pk>/remove/', views.remove_from_history, name='remove_from_history'),
] 