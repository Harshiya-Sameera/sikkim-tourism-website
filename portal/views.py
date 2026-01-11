import json
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import user_passes_test  , login_required
from .models import Incident
from .utils import analyze_cyber_risk
from google import genai
from google.genai import types
import base64
from django.contrib.auth import get_user_model
from itinerary.models import Itinerary


client = genai.Client(api_key=settings.AI_API_KEY)

# --- Authentication Views ---

def signup_view(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        passw = request.POST.get('password')
        
        if User.objects.filter(username=uname).exists():
            messages.error(request, "Username already taken.")
            return redirect('signup')
            
        user = User.objects.create_user(uname, email, passw)
        user.is_active = False  # Account remains inactive until email verification
        user.save()
        
        # Email Verification Logic
        subject = "Verify Your Sikkim Tourism Account"
        verify_url = f"http://127.0.0.1:8000/accounts/verify-otp/{uname}/"
        message = f"Hi {uname}, please use this link to verify your account: {verify_url}"
        
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            messages.success(request, "Registration successful! Please check your email to verify.")
        except Exception:
            messages.warning(request, "Account created, but email failed to send. Please contact admin.")
            
        return redirect('login')
        
    return render(request, 'auth/signup.html')

def login_view(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        passw = request.POST.get('password')
        user = authenticate(request, username=uname, password=passw)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Please verify your email first.")
        else:
            messages.error(request, "Invalid credentials.")
            
    return render(request, 'account/login.html')

def verify_email(request, username):
    try:
        user = User.objects.get(username=username)
        user.is_active = True
        user.save()
        messages.success(request, "Account verified! You can now login.")
        return redirect('login')
    except User.DoesNotExist:
        return HttpResponse("Invalid verification link.", status=404)


# --- Core Functional Views ---

def landing_view(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard') # Now this name exists in urls.py
    return render(request, 'landing.html')
    
    # Ensure this file exists at templates/portal/landing.html
    return render(request, 'portal/landing.html')


# --- Static Information Views ---

def categories_view(request):
    """Displays all tourism categories (Monasteries, Lakes, etc.)."""
    from tourism.models import Category
    categories = Category.objects.all()
    # Note: Ensure the template path matches your folder structure
    return render(request, 'portal/categories.html', {'categories': categories})

def itinerary_view(request):
    """
    Handles both the rendering of the Planner page (GET)
    and the AI itinerary generation (POST).
    """
    if request.method == 'POST':
        try:
            # 1. Extract user requirements from the AJAX call
            data = json.loads(request.body)
            days = data.get('days')
            interests = data.get('interests')
            
            # 2. Initialize Gemini 1.5 Flash for rapid planning
            # model = genai.GenerativeModel("gemini-1.5-flash")
            
            # 3. Create a strict prompt for valid JSON output
            prompt = (
                f"Role: Expert Sikkim Travel Guide. Task: Create a detailed {days}-day "
                f"itinerary based on interests: {interests}. "
                "Format: Return ONLY a raw JSON list of objects. Each object must have "
                "keys: 'day' (integer), 'time' (string), 'activity' (string), and 'location' (string). "
                "Ensure activities reflect local Sikkim culture and monasteries."
            )
            
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt
            )
            
            # 4. Clean and parse AI response
            raw_text = response.text.replace('```json', '').replace('```', '').strip()
            plan_json = json.loads(raw_text)
            
            # 5. Persistence: Save to user's profile if authenticated
            if request.user.is_authenticated:
                Itinerary.objects.create(
                    user=request.user,
                    days=days,
                    interests=interests,
                    plan_data=plan_json # Stores the list directly in JSONField
                )
                
            return JsonResponse({'plan': plan_json})

        except Exception as e:
            # Log error for admin debugging
            print(f"AI Planner Error: {e}")
            return JsonResponse({'error': str(e) + " The monk is in deep meditation. Please try again."}, status=500)
            
    # GET request simply renders the empty planner template
    return render(request, 'portal/itinerary.html')


@login_required
def user_dashboard_view(request):
    """
    User-specific view for tracking saved travel itineraries.
    """
    my_plans = Itinerary.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'plans': my_plans,
        'plan_count': my_plans.count(),
    }
    return render(request, 'dashboards/user_dashboard.html', context)

@login_required
def profile_settings_view(request):
    """
    Renders the account security and system preference interface.
    Handles the display of current user attributes and saved settings.
    """
    return render(request, 'dashboards/profile.html')

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard_view(request):
    """Central analytics dashboard for Site Administrators."""
    from tourism.models import TouristPlace, Category
    from itinerary.models import Itinerary
    
    context = {
        'total_places': TouristPlace.objects.count(),
        'total_itineraries': Itinerary.objects.count(),
        'total_users': get_user_model().objects.count(),
        'most_viewed': TouristPlace.objects.order_by('-view_count')[:5],
        'recent_users': get_user_model().objects.all().order_by('-date_joined')[:5],
    }
    return render(request, 'dashboards/admin_dashboard.html', context)

@user_passes_test(lambda u: u.is_superuser)
def user_directory_view(request):
    """View and manage all registered explorers."""
    users = get_user_model().objects.all().order_by('-date_joined')
    return render(request, 'dashboards/user_directory.html', {'users': users})


@user_passes_test(lambda u: u.is_superuser)
def admin_analytics_view(request):
    from tourism.models import TouristPlace, Category
    from django.db.models import Count
    
    # Data for Tourism Categories Distribution
    cat_counts = TouristPlace.objects.values('category__name').annotate(total=Count('id'))
    
    context = {
        'labels': [item['category__name'] for item in cat_counts],
        'data': [item['total'] for item in cat_counts],
        'total_itineraries': Itinerary.objects.count(),
    }
    return render(request, 'dashboards/analytics.html', context)


@user_passes_test(lambda u: u.is_superuser)
def ai_monitor_view(request):
    context = {
        'status': 'OPERATIONAL',
        'latency': '180ms',
        'api_usage': Itinerary.objects.count(), 
        'model': 'Gemini-1.5-Flash',
        'capabilities': ['Monastery Recognition', 'Itinerary Generation', 'Cultural Q&A'],
    }
    return render(request, 'dashboards/ai_monitor.html', context)

def map_view(request):
    """
    Fetches coordinates of all tourist spots for geographic visualization.
    """
    from tourism.models import TouristPlace
    places = TouristPlace.objects.all()
    
    context = {
        'places': places,
        'google_maps_key': settings.GOOGLE_MAPS_API_KEY # Ensure this is in your .env
    }
    return render(request, 'portal/map.html', context)

def ai_lens_view(request):
    """Renders the AI Recognition interface."""
    return render(request, 'portal/ai_lens.html')

def api_extract_image(request):
    """
    AI Lens Logic: Analyzes uploaded monastery images and 
    returns the matching place ID from our database.
    """
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            from tourism.models import TouristPlace
            image_file = request.FILES['image']
            model = genai.GenerativeModel("gemini-1.5-flash")

            image_bytes = image_file.read()
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")

            # Optimized Prompt for Tourism Recognition
            response = model.generate_content([
                "Identify this specific Sikkim monastery or landmark. Return ONLY the exact official name of the place.",
                {
                    "inline_data": {
                        "mime_type": image_file.content_type,
                        "data": image_b64
                    }
                }
            ])

            detected_name = response.text.strip()
            
            # Fuzzy search in your database of 150+ places
            place = TouristPlace.objects.filter(name__icontains=detected_name).first()
            
            if place:
                return JsonResponse({
                    'status': 'success',
                    'name': place.name,
                    'place_id': place.id,
                    'location': place.location_name
                })
            else:
                return JsonResponse({
                    'status': 'not_found',
                    'detected': detected_name
                })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

