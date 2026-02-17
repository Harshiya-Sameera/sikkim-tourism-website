import json
import google.generativeai as genai
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .models import Itinerary
from .utils import render_to_pdf
# 1. ADD THIS IMPORT AT THE TOP
from .ml_service import get_ml_recommendations 

# Configure Gemini
genai.configure(api_key=settings.AI_API_KEY)

def itinerary_view(request):
    """Handles enhanced AI itinerary generation with ML recommendations."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # --- STEP 1: PARSE DATA ---
            try:
                days = int(data.get('days', 5))
                travelers = int(data.get('travelers', 1))
            except (ValueError, TypeError):
                days = 5
                travelers = 1
                
            interests = data.get('interests', 'General Sikkim Tourism')
            weather_pref = data.get('weather', 'any')
            category_pref = data.get('category', 'sightseeing')

            # --- STEP 2: ML INTEGRATION (NEW) ---
            # Use the Content-Based Filtering model to suggest specific places
            recommended_spots = get_ml_recommendations(interests)
            spots_context = ", ".join([f"{p.name} at {p.location_name}" for p in recommended_spots])

            # --- STEP 3: SETUP AI MODEL & ENHANCED PROMPT ---
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # The prompt now combines User Inputs + ML Recommendations
            prompt = (
                f"Generate a {days}-day Sikkim travel itinerary for {travelers} travelers. "
                f"The ML model recommends these places based on similarity: {spots_context}. "
                f"User specific interests are: {interests}. "
                f"Primary Focus: {category_pref}. Preferred Weather: {weather_pref}. "
                "Output MUST be ONLY a raw JSON array of objects. "
                "Each object must contain exactly these keys: "
                "'day' (int), 'time' (string), 'activity' (string), and 'location' (string). "
                "Prioritize the ML recommended places while building the schedule. "
                "No markdown, no backticks, just raw JSON code."
            )
            
            # --- STEP 4: API CALL ---
            response = model.generate_content(prompt)
            
            if not response or not response.text:
                raise ValueError("The AI Oracle provided no response.")

            # --- STEP 5: CLEAN & PARSE ---
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            
            plan = json.loads(raw_text)
            
            # --- STEP 6: SAVE ---
            if request.user.is_authenticated:
                Itinerary.objects.create(
                    user=request.user,
                    name=f"{days} Day {category_pref.title()} Trip (Smart)",
                    days=days,
                    travelers=travelers,
                    interests=interests,
                    preferred_weather=weather_pref,
                    category_preference=category_pref,
                    plan_data=plan
                )
                
            return JsonResponse({'plan': plan})

        except Exception as e:
            print(f"\n--- [ITINERARY ML ERROR] ---\n{str(e)}\n----------------------------\n")
            return JsonResponse({'error': str(e)}, status=500)
            
    return render(request, 'portal/itinerary.html')
    
def download_itinerary_pdf(request, itinerary_id):
    """Fetches a saved itinerary and serves it as a PDF."""
    itinerary = get_object_or_404(Itinerary, id=itinerary_id)
    
    # Context to pass to the PDF template
    context = {
        'itinerary': itinerary,
        'plan': itinerary.plan_data,
        'user': itinerary.user,
    }
    
    pdf = render_to_pdf('pdf/itinerary_report.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Sikkim_Trip_{itinerary.id}.pdf"
        content = f"attachment; filename={filename}"
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Error generating PDF", status=400)