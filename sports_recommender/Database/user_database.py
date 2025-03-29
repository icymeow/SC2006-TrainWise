from django.contrib.auth.models import AbstractUser
from django.db import models

class UserDatabase(AbstractUser):
    email = models.EmailField(unique=True)
    age = models.IntegerField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    notification_enabled = models.BooleanField(default=True)
    is_first_time = models.BooleanField(default=True)
    
    # Sports preferences
    favorite_sports = models.JSONField(null=True, blank=True)
    preferred_intensity = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
        ],
        null=True,
        blank=True
    )
    preferred_weather = models.CharField(
        max_length=20,
        choices=[
            ('sunny', 'Sunny'),
            ('cloudy', 'Cloudy'),
            ('rainy', 'Rainy'),
            ('snowy', 'Snowy'),
        ],
        null=True,
        blank=True
    )
    
    def __str__(self):
        return self.email 