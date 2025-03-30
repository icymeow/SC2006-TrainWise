from django.db import models
from django.conf import settings
from apps.activities.models import Activity

class FavoriteActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'activity']
    
    def __str__(self):
        return f"{self.user.email}'s favorite: {self.activity.name}" 