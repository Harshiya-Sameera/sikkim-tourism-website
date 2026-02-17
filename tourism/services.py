import requests
from django.conf import settings

def get_weather(city_name=None, lat=None, lon=None):
    api_key = settings.OPENWEATHERMAP_API_KEY
    base_url = "https://api.openweathermap.org/data/2.5/weather"

    if lat and lon:
        params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'metric'
        }
    else:
        params = {
            'q': f"{city_name},IN",
            'appid': api_key,
            'units': 'metric'
        }

    try:
        response = requests.get(base_url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'city': data.get('name', 'Sikkim'),
                'temp': round(data['main']['temp']),
                'desc': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon'],
                'humidity': data['main']['humidity']
            }
    except Exception as e:
        print("Weather API Error:", e)

    return None
