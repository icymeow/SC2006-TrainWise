from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # ... existing urls ...
    path('delete-account/', views.delete_account, name='delete_account'),
] 