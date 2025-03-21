import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather_info(location):
    params = {
        'q': location,
        'appid': WEATHER_API_KEY,
        'units': 'metric'
    }
    response = requests.get(WEATHER_API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching weather data: {response.status_code} - {response.text}")
        return None