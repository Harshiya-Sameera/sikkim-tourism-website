from django.urls import path
from .views import ExplorePlacesView , place_detail_view

urlpatterns = [
    path('explore/', ExplorePlacesView.as_view(), name='explore_places'),
    path('place/<int:pk>/',place_detail_view, name='place_detail'),
]