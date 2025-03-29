from django.urls import path
from . import views

urlpatterns = [
    path('', views.activity_list, name='activity_list'),
    path('<int:pk>/', views.activity_detail, name='activity_detail'),
    path('<int:pk>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
] 