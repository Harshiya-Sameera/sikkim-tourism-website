# itinerary/models.py
from django.db import models
from django.conf import settings

class Itinerary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, default="My Sikkim Trip")
    days = models.IntegerField()
    travelers = models.IntegerField(default=1) # NEW
    interests = models.TextField()
    preferred_weather = models.CharField(max_length=100, blank=True, null=True) # NEW
    category_preference = models.CharField(max_length=255, blank=True, null=True) # NEW
    plan_data = models.JSONField() 
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.days} Days"