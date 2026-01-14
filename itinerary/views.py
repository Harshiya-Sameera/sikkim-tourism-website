import json
import google.generativeai as genai
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .models import Itinerary
from .utils import render_to_pdf

# Configure Gemini once at module level
genai.configure(api_key=settings.AI_API_KEY)

def itinerary_view(request):
    """Renders the planner UI and handles AI generation."""
    if request.method == 'POST':
        try:
            # 1. Parse incoming data safely
            data = json.loads(request.body)
            
            # Ensure days is an integer to match IntegerField in Models
            try:
                days = int(data.get('days', 5))
            except (ValueError, TypeError):
                days = 5
                
            interests = data.get('interests', 'General Sikkim Tourism')
            
            # 2. Setup AI Model
            # Using gemini-1.5-flash as 2.5 is not a valid model name
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # 3. Create a strict, single-output prompt
            prompt = (
                f"Generate a {days}-day Sikkim travel itinerary based on: {interests}. "
                "Output MUST be ONLY a raw JSON array of objects. "
                "Each object must contain keys: 'day' (int), 'time' (string), 'activity' (string), and 'location' (string). "
                "No markdown, no backticks, just raw JSON."
            )
            
            # 4. API Call with Response Schema for stability
            response = model.generate_content(prompt)

            
            # Check for empty response to avoid .text errors
            if not response or not response.text:
                raise ValueError("The AI Oracle provided no scroll. Please try again.")

            # 5. Safely parse JSON
            try:
                plan = json.loads(response.text)
            except json.JSONDecodeError:
                # Fallback: strip common markdown backticks if AI ignores instruction
                cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
                plan = json.loads(cleaned_text)
            
            # 6. Save to Database for logged-in explorers
            if request.user.is_authenticated:
                Itinerary.objects.create(
                    user=request.user, 
                    days=days,           # Saved as Integer
                    interests=interests, 
                    plan_data=plan       # Saved as JSONField
                )
                
            return JsonResponse({'plan': plan})

        except Exception as e:
            # IMPORTANT: This prints the exact error line to your terminal
            print(f"\n--- [ITINERARY CRITICAL ERROR] ---\n{str(e)}\n----------------------------------\n")
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