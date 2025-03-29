from django.db import models

class Activity(models.Model):
    INTENSITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    WEATHER_CHOICES = [
        ('sunny', 'Sunny'),
        ('cloudy', 'Cloudy'),
        ('rainy', 'Rainy'),
        ('snowy', 'Snowy'),
    ]
    
    ACTIVITY_TYPE_CHOICES = [
        ('indoor', 'Indoor'),
        ('outdoor', 'Outdoor'),
    ]

    facility_name = models.CharField(max_length=255)
    sports = models.CharField(max_length=255)  # Types of sports facilities
    latitude = models.FloatField()
    longitude = models.FloatField()
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_TYPE_CHOICES)
    activities = models.CharField(max_length=255)  # Specific activities available
    intensity = models.CharField(max_length=10, choices=INTENSITY_CHOICES)
    weather_conditions = models.CharField(max_length=10, choices=WEATHER_CHOICES)
    air_quality = models.IntegerField(help_text="Air Quality Index (1-500)")
    popularity = models.IntegerField(default=0, help_text="Number of times this activity has been selected")
    
    class Meta:
        verbose_name_plural = "Activities"
    
    def __str__(self):
        return f"{self.facility_name} - {self.activities}" 