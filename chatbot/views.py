# import json
# import base64
# from django.http import JsonResponse
# from django.conf import settings
# from django.shortcuts import render
# from google import genai
# from google.genai import types
# from .models import ChatConversation
# from tourism.models import TouristPlace

# # Initialize the client once
# client = genai.Client(api_key=settings.AI_API_KEY)

# def full_chat_view(request):
#     """Renders the dedicated full-screen Virtual Monk page."""
#     return render(request, 'chatbot/chatbot.html')

# def chatbot_query(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             user_msg = data.get('msg', '')
#             image_data = data.get('image', None)

#             # 1. Build the Contents List (Conditional Multimodal)
#             contents = []
#             if user_msg:
#                 contents.append(user_msg)

#             if image_data and len(image_data) > 10:
#                 # Clean base64 string
#                 if "base64," in image_data:
#                     image_data = image_data.split("base64,")[1]
                
#                 image_bytes = base64.b64decode(image_data)
#                 contents.append(
#                     types.Part.from_bytes(
#                         data=image_bytes,
#                         mime_type="image/jpeg"
#                     )
#                 )

#             if not contents:
#                 return JsonResponse({'reply': "Peace be with you. Please provide a message or an image."})

#             # 2. Single Unified System Prompt
            # system_prompt = (
            #     "Role: Virtual Monk & Sikkim Tourism Guide. "
            #     "Tone: Peaceful, helpful, and culturally knowledgeable. "
            #     "Task: Provide travel advice for Sikkim. Identify monasteries in images. "
            #     "CRITICAL: If you mention specific places, list them at the end under 'PLACES_FOUND:' "
            #     "followed by a comma-separated list of their exact names."
            # )

#             # 3. SINGLE API CALL - Use 1.5-flash for better free-tier quota stability
#             response = client.models.generate_content(
#                 model="gemini-1.5-flash",
#                 contents=contents,
#                 config=types.GenerateContentConfig(
#                     system_instruction=system_prompt,
#                     temperature=0.7,
#                 ),
#             )
            
#             bot_reply = response.text

#             # 4. Extract Places for UI Cards
#             suggested_places = []
#             if "PLACES_FOUND:" in bot_reply:
#                 parts = bot_reply.split("PLACES_FOUND:")
#                 bot_reply = parts[0].strip()
                
#                 place_names = [p.strip() for p in parts[1].split(',') if p.strip()]
#                 places_qs = TouristPlace.objects.filter(name__in=place_names)
                
#                 for p in places_qs:
#                     suggested_places.append({
#                         'id': p.id,
#                         'name': p.name,
#                         'location_name': p.location_name,
#                         'image_main': p.image_main.url if p.image_main else None,
#                         'timings': p.timings
#                     })

#             # 5. Database Logging
#             ChatConversation.objects.create(
#                 user=request.user if request.user.is_authenticated else None,
#                 message=user_msg or "[Sent Image]",
#                 response=bot_reply,
#                 is_anonymous=not request.user.is_authenticated
#             )

#             return JsonResponse({
#                 'reply': bot_reply,
#                 'places': suggested_places 
#             })
            
#         except Exception as e:
#             print(f"GenAI Error: {str(e)}")
#             return JsonResponse({
#                 'reply': "Peace be with you. Connection interrupted. Please try again.",
#                 'error': str(e)
#             }, status=500)
            
#     return JsonResponse({'error': 'Invalid request method'}, status=400)

import json
import base64
import re
import google.generativeai as genai

from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render

from .models import ChatConversation
from tourism.models import TouristPlace


# ---------------------------------------------------
# Gemini Configuration
# ---------------------------------------------------
genai.configure(api_key=settings.AI_API_KEY)


# ---------------------------------------------------
# Utility: Clean Markdown from AI Output
# ---------------------------------------------------
def clean_markdown(text):
    """
    Removes markdown symbols like **, *, headings, etc.
    Ensures clean plain-text output for UI.
    """
    if not text:
        return text

    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)   # **bold**
    text = re.sub(r'\*(.*?)\*', r'\1', text)       # *italic*
    text = re.sub(r'#+\s*', '', text)              # ### headings
    text = re.sub(r'-\s+', '', text)               # dash bullets
    return text.strip()


# ---------------------------------------------------
# Page View
# ---------------------------------------------------
def full_chat_view(request):
    """Renders the chatbot UI page"""
    return render(request, 'chatbot/chatbot.html')


# ---------------------------------------------------
# Chatbot API Endpoint
# ---------------------------------------------------
def chatbot_query(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        data = json.loads(request.body)
        user_msg = data.get('msg', '').strip()
        image_data = data.get('image')

        # ---------------------------------------------------
        # Gemini Model
        # ---------------------------------------------------
        model = genai.GenerativeModel("gemini-2.5-flash")

        # ---------------------------------------------------
        # SYSTEM PROMPT (NO MARKDOWN GUARANTEE)
        # ---------------------------------------------------
        system_prompt = (
            "Role: Virtual Monk & Sikkim Tourism Guide. "
            "Tone: Peaceful, helpful, and culturally knowledgeable. "
            "Task: Provide travel advice for Sikkim and identify monasteries in images. "
            "IMPORTANT OUTPUT RULES: "
            "1. Do NOT use Markdown. "
            "2. Do NOT use **, *, bullets, or headings. "
            "3. Use plain text only. "
            "4. Use numbered points like 1., 2., 3. "
            "CRITICAL: If places are mentioned, list them at the end under "
            "'PLACES_FOUND:' followed by a comma-separated list of exact names."
        )

        # ---------------------------------------------------
        # Build Input (Text + Image)
        # ---------------------------------------------------
        contents = [system_prompt]

        if user_msg:
            contents.append(user_msg)

        if image_data:
            if "base64," in image_data:
                image_data = image_data.split("base64,")[1]

            image_bytes = base64.b64decode(image_data)
            contents.append({
                "mime_type": "image/jpeg",
                "data": image_bytes
            })

        if len(contents) == 1:
            return JsonResponse({'reply': 'Please enter a message or upload an image.'})

        # ---------------------------------------------------
        # Generate AI Response
        # ---------------------------------------------------
        response = model.generate_content(contents)
        raw_reply = response.text or ""

        # ---------------------------------------------------
        # Clean Markdown
        # ---------------------------------------------------
        bot_reply = clean_markdown(raw_reply)

        # ---------------------------------------------------
        # Extract PLACES_FOUND
        # ---------------------------------------------------
        suggested_places = []

        if "PLACES_FOUND:" in bot_reply:
            reply_part, places_part = bot_reply.split("PLACES_FOUND:", 1)
            bot_reply = reply_part.strip()

            place_names = [p.strip() for p in places_part.split(',') if p.strip()]
            places_qs = TouristPlace.objects.filter(name__in=place_names)

            for p in places_qs:
                suggested_places.append({
                    "id": p.id,
                    "name": p.name,
                    "location_name": p.location_name,
                    "image_main": p.image_main.url if p.image_main else None,
                    "timings": p.timings
                })

        # ---------------------------------------------------
        # Save Conversation
        # ---------------------------------------------------
        ChatConversation.objects.create(
            user=request.user if request.user.is_authenticated else None,
            message=user_msg or "[Image Uploaded]",
            response=bot_reply,
            is_anonymous=not request.user.is_authenticated
        )

        # ---------------------------------------------------
        # Final Response
        # ---------------------------------------------------
        return JsonResponse({
            "reply": bot_reply,
            "places": suggested_places
        })

    except Exception as e:
        print("Chatbot Error:", str(e))
        return JsonResponse(
            {'reply': 'Peace be with you. Something went wrong. Please try again.'},
            status=500
        )
