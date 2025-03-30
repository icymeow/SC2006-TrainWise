from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    age = models.IntegerField(null=True, blank=True)
    preferences = models.JSONField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    notification_enabled = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email 