from django.views.generic import ListView
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import TouristPlace, Category
from django.core.serializers import serialize
from django.http import HttpResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D # REQUIRED for distance lookups

class ExplorePlacesView(ListView):
    model = TouristPlace
    template_name = 'tourism/explore.html'
    context_object_name = 'places'
    paginate_by = 12 

    def get_queryset(self):
        # 1. Start with the base queryset
        queryset = super().get_queryset()
        
        # 2. Get Search and Filter Parameters
        query = self.request.GET.get('q')
        category_name = self.request.GET.get('category')
        lat = self.request.GET.get('lat')
        lng = self.request.GET.get('lng')

        # 3. Apply Text Search
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        # 4. Apply Category Filtering
        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)
            
        # 5. Apply Proximity Sorting (GeoDjango)
        if lat and lng:
            try:
                # Convert to float and create a Point object
                user_location = Point(float(lng), float(lat), srid=4326)
                
                # Annotate distance and sort by closest first
                queryset = queryset.annotate(
                    dist_obj=Distance('location', user_location)
                ).order_by('dist_obj')
            except (ValueError, TypeError):
                # If coordinates are invalid, just return the standard list
                pass
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass categories for the filter buttons in the UI
        context['categories'] = Category.objects.all()
        # Keep track of current category for active button styling
        context['current_category'] = self.request.GET.get('category', 'All')
        return context

def place_detail_view(request, pk):
    place = get_object_or_404(TouristPlace, pk=pk)
    place.view_count += 1
    place.save()
    
    nearby_hotels = ["Hotel Sikkim Delight", "Himalayan Retreat Lodge", "The Royal Monastery Inn"]
    
    # Spatial Query: Find spots within 20km of THIS place
    nearby_spots = TouristPlace.objects.filter(
        location__distance_lte=(place.location, D(km=20))
    ).exclude(id=pk)[:3]
    
    context = {
        'place': place,
        'nearby_hotels': nearby_hotels,
        'nearby_spots': nearby_spots,
        'google_maps_key': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, 'tourism/place_detail.html', context)

def tourist_place_geojson(request):
    """Returns all tourist places as GeoJSON."""
    data = serialize('geojson', TouristPlace.objects.all())
    return HttpResponse(data, content_type='application/json')

class NearbyPlacesView(ListView):
    model = TouristPlace
    template_name = 'tourism/nearby.html'
    context_object_name = 'nearby_places'

    def get_queryset(self):
        # Example: Coordinates for Gangtok center
        user_lat = self.request.GET.get('lat', 27.3314)
        user_lng = self.request.GET.get('lng', 88.6138)
        
        user_location = Point(float(user_lng), float(user_lat), srid=4326)
        
        # Filter places within 10km and annotate them with the exact distance
        return TouristPlace.objects.filter(
            location__distance_lte=(user_location, D(km=10))
        ).annotate(
            distance=Distance('location', user_location)
        ).order_by('distance')
    