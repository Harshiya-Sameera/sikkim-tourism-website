import json
import base64
from django import forms
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
from .models import ChatConversation
from tourism.models import TouristPlace

# NEW: Import the updated SDK
from google import genai
from google.genai import types

# Initialize the Client
client = genai.Client(api_key=settings.AI_API_KEY)

def full_chat_view(request):
    """Renders the dedicated full-screen Virtual Monk page."""
    return render(request, 'chatbot/chatbot.html')

def chatbot_query(request):
    """API endpoint for AI Wisdom and Monastery detection using google-genai."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_msg = data.get('msg', '')
            image_data = data.get('image', None)  # Expecting base64 string
            
            # SYSTEM INSTRUCTION: Tourism Guide Persona
            system_prompt = (
                "Role: Virtual Monk & Sikkim Tourism Guide. "
                "Tone: Peaceful, helpful, and culturally knowledgeable. "
                "Task: Provide travel advice for Sikkim. If an image is provided, identify the monastery. "
                "CRITICAL: If you mention specific places, list them at the end of your message "
                "under the label 'PLACES_FOUND:' followed by a comma-separated list of their exact names."
            )

            # Build content list
            # The new SDK separates system instructions into a specific config parameter
            contents = []
            if user_msg:
                contents.append(user_msg)
            
            if image_data:
                # If image_data is a base64 string, convert to bytes
                contents.append(
                    types.Part.from_bytes(
                        data=base64.b64decode(image_data),
                        mime_type="image/jpeg"
                    )
                )

            # Call the new SDK
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                ),
            )
            
            bot_reply = response.text

            # Logic to extract mentioned places for UI Cards
            suggested_places = []
            if "PLACES_FOUND:" in bot_reply:
                parts = bot_reply.split("PLACES_FOUND:")
                bot_reply = parts[0].strip() 
                place_names = [p.strip() for p in parts[1].split(',')]
                suggested_places = list(TouristPlace.objects.filter(name__in=place_names).values(
                    'id', 'name', 'location_name', 'image_main', 'timings'
                ))

            # Log to Database
            ChatConversation.objects.create(
                user=request.user if request.user.is_authenticated else None,
                message=user_msg if user_msg else "Image Evidence",
                response=bot_reply,
                is_anonymous=not request.user.is_authenticated
            )

            return JsonResponse({
                'reply': bot_reply,
                'places': suggested_places 
            })
            
        except Exception as e:
            print(f"Error: {e}") # Log error for debugging
            return JsonResponse({'reply': "Peace be with you. My connection is currently interrupted. Please try again later."}, status=500)
            
    return JsonResponse({'error': 'Invalid request'}, status=400)