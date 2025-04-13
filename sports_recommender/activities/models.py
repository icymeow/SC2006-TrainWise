from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Activity(models.Model):
    """Model representing a sports activity or facility."""
    
    ACTIVITY_TYPES = [
        ('GYM', 'Gym'),
        ('SWIMMING', 'Swimming'),
        ('RUNNING', 'Running'),
        ('BASKETBALL', 'Basketball'),
        ('FOOTBALL', 'Football'),
        ('TENNIS', 'Tennis'),
        ('BADMINTON', 'Badminton'),
        ('TABLE_TENNIS', 'Table Tennis'),
        ('VOLLEYBALL', 'Volleyball'),
        ('SQUASH', 'Squash'),
        ('HOCKEY', 'Hockey'),
        ('PICKLEBALL', 'Pickleball'),
        ('NETBALL', 'Netball'),
        ('LAWN_BOWL', 'Lawn Bowl'),
        ('OTHER', 'Other'),
    ]
    
    INTENSITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]
    
    facility_name = models.CharField(max_length=200)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    intensity = models.CharField(max_length=10, choices=INTENSITY_LEVELS)
    is_indoor = models.BooleanField(default=False)
    image_url = models.URLField(blank=True, null=True)
    address = models.CharField(max_length=500)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    operating_hours = models.CharField(max_length=200)
    price_range = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.facility_name} - {self.get_activity_type_display()}"

    class Meta:
        verbose_name_plural = "Activities"
        ordering = ['facility_name']

class ActivityHistory(models.Model):
    """Model representing a user's workout history for an activity."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    date_completed = models.DateField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    duration = models.DurationField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity.facility_name} on {self.date_completed}"

    class Meta:
        verbose_name_plural = "Activity histories"
        ordering = ['-date_completed']

class FavoriteActivity(models.Model):
    """Model representing a user's favorite activities."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity.facility_name}"

    class Meta:
        verbose_name_plural = "Favorite activities"
        unique_together = ['user', 'activity']
        ordering = ['activity__facility_name']

class UserPreference(models.Model):
    """Model for storing user preferences for activity recommendations."""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]

    ACTIVITY_CHOICES = [
        ('running', 'Running/Jogging/Walking'),
        ('swimming', 'Swimming'),
        ('badminton', 'Badminton'),
        ('basketball', 'Basketball'),
        ('tennis', 'Tennis'),
        ('table_tennis', 'Table Tennis'),
        ('volleyball', 'Volleyball'),
        ('pickleball', 'Pickleball'),
        ('gym', 'Gym'),
        ('soccer', 'Soccer'),
        ('squash', 'Squash'),
        ('netball', 'Netball'),
        ('lawn_bowl', 'Lawn Bowl'),
        ('hockey', 'Hockey'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    preferred_activity_types = models.CharField(max_length=200, help_text="Comma-separated list of activity types", blank=True)
    max_distance = models.DecimalField(max_digits=5, decimal_places=2, help_text="Maximum distance in kilometers", default=10.0)
    indoor_preference = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_preferred_activity_types(self):
        """Convert stored comma-separated string into a list of activity types."""
        if not self.preferred_activity_types:
            return []
        # Split by comma and clean up any whitespace
        activities = [act.strip() for act in self.preferred_activity_types.split(',') if act.strip()]
        # Ensure all activities are valid choices
        valid_activities = [choice[0] for choice in self.ACTIVITY_CHOICES]
        return [act for act in activities if act in valid_activities]

    def set_preferred_activity_types(self, activities):
        """Store activity types as a comma-separated string."""
        if not activities:
            self.preferred_activity_types = ''
            return
        
        # Ensure all activities are valid choices
        valid_activities = [choice[0] for choice in self.ACTIVITY_CHOICES]
        valid_list = [act for act in activities if act in valid_activities]
        self.preferred_activity_types = ','.join(valid_list)

    def __str__(self):
        return f"{self.user.username}'s preferences"

    class Meta:
        verbose_name_plural = "User preferences"
        ordering = ['user__username'] 