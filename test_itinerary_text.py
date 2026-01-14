from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()  # <-- THIS LINE IS CRITICAL

client = genai.Client(api_key=os.getenv("AI_API_KEY"))

PROMPT = """
Generate a 3-day Sikkim itinerary for interests: Monasteries, Nature.
Return ONLY raw JSON array.
Each object must contain:
day (int), time (string), activity (string), location (string).
"""

response = client.models.generate_content(
    model="models/gemini-flash-latest",
    contents=PROMPT,
    config={
        "response_mime_type": "application/json",
        "temperature": 0.7
    }
)

print(response.text)
print(json.loads(response.text))
