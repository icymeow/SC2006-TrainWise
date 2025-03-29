from django.db import models

class Activity(models.Model):
    INTENSITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    WEATHER_CONDITIONS = [
        ('sunny', 'Sunny'),
        ('cloudy', 'Cloudy'),
        ('rainy', 'Rainy'),
        ('snowy', 'Snowy'),
    ]
    
    name = models.CharField(max_length=200)
    venue_name = models.CharField(max_length=200)
    description = models.TextField()
    activity_type = models.CharField(max_length=100)
    intensity_level = models.CharField(max_length=10, choices=INTENSITY_CHOICES)
    suitable_weather = models.CharField(max_length=10, choices=WEATHER_CONDITIONS)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} at {self.venue_name}" 