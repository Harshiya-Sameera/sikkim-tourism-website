from django.views.generic import ListView
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import TouristPlace, Category

class ExplorePlacesView(ListView):
    model = TouristPlace
    template_name = 'tourism/explore.html'
    context_object_name = 'places'
    paginate_by = 12 

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        category_name = self.request.GET.get('category') # Using name as per your template link

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context 

def place_detail_view(request, pk):
    place = get_object_or_404(TouristPlace, pk=pk)
    place.view_count += 1
    place.save()
    
    # Static data for presentation - can be moved to models later
    nearby_hotels = ["Hotel Sikkim Delight", "Himalayan Retreat Lodge", "The Royal Monastery Inn"]
    nearby_spots = TouristPlace.objects.filter(category=place.category).exclude(id=pk)[:3]
    
    context = {
        'place': place,
        'nearby_hotels': nearby_hotels,
        'nearby_spots': nearby_spots,
        'google_maps_key': settings.GOOGLE_MAPS_API_KEY # Pulled from settings.py
    }
    return render(request, 'tourism/place_detail.html', context)