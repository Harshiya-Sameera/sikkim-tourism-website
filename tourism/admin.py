from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from .models import Category, TouristPlace

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
@admin.register(TouristPlace)
class TouristPlaceAdmin(LeafletGeoAdmin):  # CHANGED: Inherit from LeafletGeoAdmin
    list_display = ('name', 'category', 'location_name', 'is_featured', 'view_count')
    list_filter = ('category', 'is_featured')
    search_fields = ('name', 'location_name', 'description')
    list_editable = ('is_featured',)
    
    # Optional: Configure how the map behaves specifically for this admin
    # This override will center the map on Gangtok when adding a new place
    settings_overrides = {
        'DEFAULT_CENTER': (27.3314, 88.6138),  # Sikkim coordinates
        'DEFAULT_ZOOM': 10,
    }