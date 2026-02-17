import json
import base64
import math
from urllib import request

from google import genai

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.db.models import Count
from django.core.serializers import serialize

from django.contrib.gis.geos import Point

from itinerary.models import Itinerary
from tourism.models import TouristPlace, Category, SavedPlace

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ============================================================
# GEMINI CONFIGURATION (ONLY ONE – CORRECT)
# ============================================================

client = genai.Client(api_key=settings.AI_API_KEY)

# ============================================================
# CORE VIEWS
# ============================================================

def landing_view(request):
    featured = TouristPlace.objects.filter(is_featured=True)[:6]
    return render(request, 'landing.html', {'featured': featured})


def categories_view(request):
    return render(request, 'portal/categories.html', {
        'categories': Category.objects.all(),
        'page_type': 'categories'
    })


# ============================================================
# ITINERARY (AI)
# ============================================================

def itinerary_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            days = int(data.get('days', 5))
            interests = data.get('interests', 'Sikkim Tourism')

            response = client.models.generate_content(
                model="models/gemini-flash-latest",
                contents=(
                    f"Generate a {days}-day Sikkim itinerary for interests: {interests}. "
                    "Return ONLY raw JSON array. Each object must contain: "
                    "day (int), time (string), activity (string), location (string)."
                ),
                config={
                    "response_mime_type": "application/json",
                    "temperature": 0.7
                }
            )

            plan = json.loads(response.text)

            if request.user.is_authenticated:
                Itinerary.objects.create(
                    user=request.user,
                    name=f"{days} Days in Sikkim ({interests})", # Add this
                    days=days,
                    interests=interests,
                    plan_data=plan
                )

            return JsonResponse({'plan': plan})

        except Exception as e:
            print("ITINERARY ERROR:", str(e))
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'portal/itinerary.html', {'page_type': 'itinerary'})


# ============================================================
# MAP + GEO DATA
# ============================================================

def map_view(request):
    return render(request, 'portal/map.html', {
        'places': TouristPlace.objects.all(),
        'google_maps_key': settings.GOOGLE_MAPS_API_KEY,
        'page_type': 'map'
    })


def places_geojson(request):
    data = serialize(
        'geojson',
        TouristPlace.objects.all(),
        geometry_field='location',
        fields=('name', 'location_name', 'pk')
    )
    return HttpResponse(data, content_type='application/json')


# ============================================================
# AI LENS – IMAGE RECOGNITION
# ============================================================

def ai_lens_view(request):
    return render(request, 'portal/ai_lens.html', {'page_type': 'ai_lens'})


def api_extract_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image_file = request.FILES['image']
            image_b64 = base64.b64encode(image_file.read()).decode()

            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    "Identify this Sikkim landmark. Return ONLY the name.",
                    {
                        "inline_data": {
                            "mime_type": image_file.content_type,
                            "data": image_b64
                        }
                    }
                ]
            )

            detected = response.text.strip()

            place = TouristPlace.objects.filter(
                name__icontains=detected
            ).first()

            if place:
                place.view_count += 1
                place.save()
                return JsonResponse({
                    'status': 'success',
                    'name': place.name,
                    'place_id': place.id,
                    'category': place.category.name
                })

            return JsonResponse({'status': 'not_found', 'detected': detected})

        except Exception as e:
            print("AI LENS ERROR:", str(e))
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


# ============================================================
# USER DASHBOARD
# ============================================================

@login_required
def user_dashboard_view(request):
    # 1. DEFINE my_plans (This line was missing)
    my_plans = Itinerary.objects.filter(user=request.user).order_by('-created_at')
    
    # 2. Fetch Saved Places (Ensure SavedPlace is imported at the top)
    saved_places = SavedPlace.objects.filter(user=request.user).select_related('place')
    
    context = {
        'plans': my_plans,           # This now refers to the variable above
        'plan_count': my_plans.count(),
        'saved_places': saved_places,
        'saved_count': saved_places.count(),
    }
    return render(request, 'dashboards/user_dashboard.html', context)


@login_required
def profile_settings_view(request):
    return render(request, 'dashboards/profile.html')

def view_plan_detail(request, plan_id):
    # Retrieve the specific plan or return a 404 error
    plan = get_object_or_404(Itinerary, id=plan_id, user=request.user)
    
    return render(request, 'dashboards/view_plan.html', {
        'plan': plan
    })

# ============================================================
# ADMIN DASHBOARD
# ============================================================

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard_view(request):
    from django.utils import timezone
    from datetime import timedelta

    last_week = timezone.now() - timedelta(days=7)

    return render(request, 'dashboards/admin_dashboard.html', {
        'total_places': TouristPlace.objects.count(),
        'total_itineraries': Itinerary.objects.count(),
        'total_users': get_user_model().objects.count(),
        'recent_plans': Itinerary.objects.filter(created_at__gte=last_week).count(),
        'top_sites': TouristPlace.objects.order_by('-view_count')[:5],
        'categories': Category.objects.annotate(place_count=Count('places')),
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_analytics_view(request):
    categories = Category.objects.annotate(total=Count('places'))
    popular = TouristPlace.objects.order_by('-view_count')[:7]

    return render(request, 'dashboards/analytics.html', {
        'cat_labels': [c.name for c in categories],
        'cat_counts': [c.total for c in categories],
        'place_labels': [p.name for p in popular],
        'place_views': [p.view_count for p in popular],
        'total_itineraries': Itinerary.objects.count(),
        'total_users': get_user_model().objects.count(),
    })


@user_passes_test(lambda u: u.is_superuser)
def ai_monitor_view(request):
    return render(request, 'dashboards/ai_monitor.html', {
        'status': 'OPERATIONAL',
        'latency': '180ms',
        'model': 'Gemini-1.5-Flash',
        'api_usage': Itinerary.objects.count(),
        'capabilities': [
            'Vision Recognition',
            'Itinerary Generation',
            'Cultural Q&A'
        ]
    })


@user_passes_test(lambda u: u.is_superuser)
def user_directory_view(request):
    return render(request, 'dashboards/user_directory.html', {
        'users': get_user_model().objects.all()
    })


@user_passes_test(lambda u: u.is_superuser)
def manage_places_view(request):
    return render(request, 'dashboards/manage_places.html', {
        'places': TouristPlace.objects.all().order_by('name')
    })


@user_passes_test(lambda u: u.is_superuser)
def delete_place(request, pk):
    place = get_object_or_404(TouristPlace, pk=pk)
    if request.method == 'POST':
        place.delete()
        messages.success(request, f"{place.name} removed successfully.")
    return redirect('admin_manage_places')


@user_passes_test(lambda u: u.is_superuser)
def admin_chat_logs_view(request):
    from chatbot.models import ChatConversation
    logs = ChatConversation.objects.all().order_by('-timestamp')[:50]
    return render(request, 'dashboards/admin_chat_logs.html', {'logs': logs})


@user_passes_test(lambda u: u.is_superuser)
def toggle_user_status(request, user_id):
    user = get_object_or_404(get_user_model(), id=user_id)
    if user != request.user:
        user.is_active = not user.is_active
        user.save()
    return redirect('admin_user_management')


@user_passes_test(lambda u: u.is_superuser)
def delete_explorer(request, user_id):
    user = get_object_or_404(get_user_model(), id=user_id)
    if user != request.user:
        user.delete()
    return redirect('admin_user_management')


@user_passes_test(lambda u: u.is_superuser)
def bulk_upload_places(request):
    if request.method == 'POST' and request.FILES.get('json_file'):
        file = request.FILES['json_file']
        data = json.load(file)

        # ✅ FIX: read places array correctly
        places = data.get('places', [])

        if not isinstance(places, list):
            messages.error(request, "Invalid JSON format.")
            return redirect('admin_manage_places')

        for item in places:
            # 1. Category
            cat_obj, _ = Category.objects.get_or_create(
                name=item.get('category')
            )

            # 2. Place
            TouristPlace.objects.get_or_create(
                name=item.get('name'),
                defaults={
                    'category': cat_obj,
                    'location_name': item.get('location_name'),
                    'description': item.get('description'),
                    'history': item.get('history'),
                    'location': Point(item.get('lng'), item.get('lat')),
                    'timings': item.get('timings'),
                    'entry_fee': item.get('entry_fee', 0)
                }
            )

        messages.success(request, "Places imported successfully.")
        return redirect('admin_manage_places')

    return render(request, 'dashboards/bulk_upload.html')


@login_required
def toggle_save_place(request, place_id):
    place = get_object_or_404(TouristPlace, id=place_id)
    saved_item, created = SavedPlace.objects.get_or_create(user=request.user, place=place)
    
    if not created:
        saved_item.delete()
        message = "Removed from your trip."
        action = "removed"
    else:
        message = "Added to your trip planner!"
        action = "added"
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'action': action, 'message': message})
    
    messages.success(request, message)
    return redirect('place_detail', pk=place_id)

def explore_view(request):
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    query = request.GET.get('q')
    category_name = request.GET.get('category')

    places = TouristPlace.objects.all()

    if category_name and category_name != "All":
        places = places.filter(category__name=category_name)

    if query:
        places = places.filter(name__icontains=query)

    # -------- DISTANCE LOGIC (SQLITE SAFE) --------
    if lat and lng:
        try:
            user_lat = float(lat)
            user_lng = float(lng)

            place_list = []

            for place in places:
                if place.location:
                    place_lat = place.location.y
                    place_lng = place.location.x

                    distance_km = haversine(
                        user_lat,
                        user_lng,
                        place_lat,
                        place_lng
                    )

                    place.distance_km = round(distance_km, 1)
                else:
                    place.distance_km = None

                place_list.append(place)

            # Sort by distance (None values go last)
            place_list.sort(
                key=lambda x: x.distance_km if x.distance_km is not None else 9999
            )

            places = place_list

        except Exception:
            places = places.order_by('-view_count')
    else:
        places = places.order_by('-view_count')

    context = {
        'places': places,
        'categories': Category.objects.all(),
    }
    return render(request, 'portal/explore.html', context)