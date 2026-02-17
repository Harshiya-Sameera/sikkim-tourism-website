from django.db import models
from django.contrib.gis.db import models as gis_models
from django.conf import settings


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    location = gis_models.PointField(srid=4326, null=True, blank=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    price_range = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    # This matches the migration you just ran
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    icon_class = models.CharField(max_length=50, default="fa-om")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class TouristPlace(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='places')
    description = models.TextField()
    history = models.TextField()
    image_main = models.ImageField(upload_to='places/main/')
    timings = models.CharField(max_length=100)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    location = gis_models.PointField(
        srid=4326,
        null=True,
        blank=True
    )
    location_name = models.CharField(max_length=255)
    how_to_reach = models.TextField()
    best_time_to_visit = models.CharField(max_length=200)
    is_featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    nearby_hotels = models.JSONField(blank=True, null=True)


    def __str__(self):
        return self.name

class SavedPlace(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    place = models.ForeignKey(TouristPlace, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'place')