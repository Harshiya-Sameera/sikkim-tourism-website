import json
from django.views.generic import ListView
from django.db.models import Q, F
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.serializers import serialize
from django.http import HttpResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.core.cache import cache

from .models import Hotel, TouristPlace, Category
from .services import get_weather


# ==========================================================
# EXPLORE VIEW
# ==========================================================

class ExplorePlacesView(ListView):
    model = TouristPlace
    template_name = 'tourism/explore.html'
    context_object_name = 'places'
    paginate_by = 12

    def get_queryset(self):
        queryset = TouristPlace.objects.select_related('category').all()

        # Get parameters
        query = self.request.GET.get('q')
        category_name = self.request.GET.get('category')
        lat = self.request.GET.get('lat')
        lng = self.request.GET.get('lng')

        # --------------------------------------------------
        # Text Search
        # --------------------------------------------------
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )

        # --------------------------------------------------
        # Category Filter (Safe Handling of "All")
        # --------------------------------------------------
        if category_name and category_name != 'All':
            queryset = queryset.filter(
                category__name__iexact=category_name
            )

        # --------------------------------------------------
        # Geo Proximity Sorting
        # --------------------------------------------------
        if lat and lng:
            try:
                lat = float(lat)
                lng = float(lng)

                user_location = Point(lng, lat, srid=4326)

                queryset = queryset.annotate(
                    distance=Distance('location', user_location)
                ).order_by('distance')

            except (ValueError, TypeError):
                queryset = queryset.order_by('-view_count', 'name')
        else:
            queryset = queryset.order_by('-view_count', 'name')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category', 'All')
        context['search_query'] = self.request.GET.get('q', '')

        # --------------------------------------------------
        # Cached Weather (Gangtok Hub)
        # --------------------------------------------------
        weather_data = cache.get('sikkim_weather_gangtok')

        if not weather_data:
            weather_data = get_weather("Gangtok")
            cache.set('sikkim_weather_gangtok', weather_data, 1800)

        context['weather'] = weather_data

        return context


# ==========================================================
# PLACE DETAIL VIEW
# ==========================================================

def place_detail_view(request, pk):

    # Atomic increment (thread safe)
    TouristPlace.objects.filter(pk=pk).update(
        view_count=F('view_count') + 1
    )

    place = get_object_or_404(
        TouristPlace.objects.select_related('category'),
        pk=pk
    )

    # --------------------------------------------------
    # Cached Local Weather
    # --------------------------------------------------
    weather_cache_key = f'weather_place_{pk}'
    weather = cache.get(weather_cache_key)

    if not weather:
        weather = get_weather(place.location_name)
        cache.set(weather_cache_key, weather, 1800)

    # --------------------------------------------------
    # Nearby Spots (20km radius)
    # --------------------------------------------------
    nearby_spots = TouristPlace.objects.filter(
        location__distance_lte=(place.location, D(km=20))
    ).exclude(pk=pk).annotate(
        distance=Distance('location', place.location)
    ).order_by('distance')[:3]

    nearby_hotels = Hotel.objects.filter(
        location__distance_lte=(place.location, D(km=10))
    ).annotate(
        distance=Distance('location', place.location)
    ).order_by('distance')[:5]

    context = {
        'place': place,
        'weather': weather,
        'nearby_hotels': nearby_hotels,
        'nearby_spots': nearby_spots,
        'google_maps_key': settings.GOOGLE_MAPS_API_KEY
    }

    return render(request, 'tourism/place_detail.html', context)


# ==========================================================
# GEOJSON MAP DATA
# ==========================================================

def tourist_place_geojson(request):
    """
    Returns all tourist places as GeoJSON
    Used for global interactive map
    """
    data = serialize(
        'geojson',
        TouristPlace.objects.all(),
        geometry_field='location',
        fields=('name', 'description')
    )
    return HttpResponse(data, content_type='application/json')


# ==========================================================
# NEARBY PLACES VIEW
# ==========================================================

class NearbyPlacesView(ListView):
    model = TouristPlace
    template_name = 'tourism/nearby.html'
    context_object_name = 'nearby_places'

    def get_queryset(self):

        lat = self.request.GET.get('lat', 27.3314)
        lng = self.request.GET.get('lng', 88.6138)

        try:
            lat = float(lat)
            lng = float(lng)

            user_location = Point(lng, lat, srid=4326)

            queryset = TouristPlace.objects.filter(
                location__distance_lte=(user_location, D(km=10))
            ).annotate(
                distance=Distance('location', user_location)
            ).order_by('distance')

            return queryset

        except (ValueError, TypeError):
            return TouristPlace.objects.none()
