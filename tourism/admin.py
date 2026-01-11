from django.contrib import admin
from .models import Category, TouristPlace

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(TouristPlace)
class TouristPlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'location_name', 'is_featured', 'view_count')
    list_filter = ('category', 'is_featured')
    search_fields = ('name', 'location_name', 'description')
    # This allows you to toggle "Featured" status directly from the list view
    list_editable = ('is_featured',)