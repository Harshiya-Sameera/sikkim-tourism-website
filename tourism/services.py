import requests
from django.conf import settings

def get_weather(city_name):
    """
    One method to fetch weather for any location in Sikkim.
    Usage: weather = get_weather("Gangtok")
    """
    api_key = settings.OPENWEATHERMAP_API_KEY # Add this to settings.py
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        'q': f"{city_name},IN", # Filters for India
        'appid': api_key,
        'units': 'metric' # Returns Celsius
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'temp': round(data['main']['temp']),
                'desc': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon'],
                'humidity': data['main']['humidity']
            }
    except Exception as e:
        print(f"Weather API Error: {e}")
    
    # Fallback if API fails
    return {'temp': '--', 'desc': 'Cloudy', 'icon': '01d', 'humidity': '--'}