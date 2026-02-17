from django.urls import path
from .views import explore_view, place_detail_view, tourist_place_geojson

urlpatterns = [
    path('explore/', explore_view, name='explore_places'),
    path('place/<int:pk>/', place_detail_view, name='place_detail'),
    path('api/places/', tourist_place_geojson, name='places_geojson'),
]
