import json
import base64
import re
from django.db.models import Q
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
    if not text:
        return text

    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'-\s+', '', text)

    return text.strip()


# ---------------------------------------------------
# Page View
# ---------------------------------------------------
def full_chat_view(request):
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
        # Direct Database Match (Structured Response)
        # ---------------------------------------------------
        suggested_places = []

        if user_msg:
            stop_words = {"tell", "me", "about", "the", "is", "what", "where", "show", "details", "information"}

            keywords = [
                w for w in user_msg.lower().split()
                if w not in stop_words
            ]

            query = Q()
            for word in keywords:
                query |= Q(name__icontains=word)

            matched_places = TouristPlace.objects.filter(query).distinct()

            for p in matched_places:
                suggested_places.append({
                    "id": p.id,
                    "name": p.name,
                    "location_name": p.location_name,
                    "image_main": p.image_main.url if p.image_main else None,
                    "timings": p.timings
                })

        # ---------------------------------------------------
        # Gemini Model
        # ---------------------------------------------------
        model = genai.GenerativeModel("gemini-2.5-flash")

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

        bot_reply = clean_markdown(raw_reply)

        # ---------------------------------------------------
        # AI-Based Place Extraction (Fallback)
        # ---------------------------------------------------
        if "PLACES_FOUND:" in bot_reply:
            reply_part, places_part = bot_reply.split("PLACES_FOUND:", 1)
            bot_reply = reply_part.strip()

            place_names = [p.strip() for p in places_part.split(',') if p.strip()]
            places_qs = TouristPlace.objects.filter(name__in=place_names)

            for p in places_qs:
                if not any(sp["id"] == p.id for sp in suggested_places):
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
        # Final Structured JSON Response
        # ---------------------------------------------------
        return JsonResponse({
            "reply": bot_reply,
            "places": suggested_places,
            "structured": True if suggested_places else False
        })

    except Exception as e:
        print("Chatbot Error:", str(e))
        return JsonResponse(
            {
                "reply": "Peace be with you. Something went wrong. Please try again."
            },
            status=500
        )
