from django.urls import path
from . import views

urlpatterns = [
    path('favorites/', views.favorite_activities, name='favorites'),
    path('recommended/', views.recommended_activities, name='recommended'),
] 