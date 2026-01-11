from django.db import models

class Category(models.Model):
    """Categories like Monasteries, Lakes, Viewpoints, etc."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class TouristPlace(models.Model):
    """Core model for the 150+ tourist locations in Sikkim."""
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='places')
    description = models.TextField()
    history = models.TextField(help_text="Cultural and historical background of the place.")
    
    # Media and logistics
    image_main = models.ImageField(upload_to='places/main/')
    timings = models.CharField(max_length=100, help_text="Example: 9:00 AM - 6:00 PM")
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Location data for Google Maps & Route planning
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_name = models.CharField(max_length=255, help_text="District or nearby town")
    how_to_reach = models.TextField(help_text="Details on travel via bus, taxi, or trekking.")
    best_time_to_visit = models.CharField(max_length=200)
    
    # Search and Analytics
    is_featured = models.BooleanField(default=False, help_text="Show on landing page")
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name