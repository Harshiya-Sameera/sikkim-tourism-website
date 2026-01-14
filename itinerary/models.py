from django.db import models
from django.conf import settings

class Itinerary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, default="My Sikkim Trip")
    days = models.IntegerField()
    interests = models.TextField()
    plan_data = models.JSONField() # Stores the day-wise slots
    created_at = models.DateTimeField(auto_now_add=True)
    # If this is named 'description' instead of 'content':
    description = models.TextField()

    def __str__(self):
        return f"{self.title} - {self.days} Days"
    