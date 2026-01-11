import json
import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from .models import Itinerary

genai.configure(api_key=settings.AI_API_KEY)

def itinerary_view(request):
    """Renders the planner UI and handles AI generation."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            days = data.get('days')
            interests = data.get('interests')
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = (
                f"Generate a {days}-day Sikkim travel itinerary for interests: {interests}. "
                "Format as a JSON list of objects, each with 'day', 'time', 'activity', and 'location'."
                "Return ONLY the raw JSON."
            )
            
            response = model.generate_content(prompt)
            plan = json.loads(response.text.replace('```json', '').replace('```', '').strip())
            
            # Optionally save to DB if user is logged in
            if request.user.is_authenticated:
                Itinerary.objects.create(
                    user=request.user, days=days, interests=interests, plan_data=plan
                )
                
            return JsonResponse({'plan': plan})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return render(request, 'portal/itinerary.html')