from django.urls import path
from .views import ExplorePlacesView, place_detail_view, tourist_place_geojson
urlpatterns = [
    path('explore/', ExplorePlacesView.as_view(), name='explore_places'),
    path('place/<int:pk>/',place_detail_view, name='place_detail'),
    path('api/places/', tourist_place_geojson, name='places_geojson'),
]