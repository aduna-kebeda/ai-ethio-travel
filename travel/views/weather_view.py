from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from travel.utils.weather_utils import get_weather_info

@api_view(['GET'])
def fetch_weather(request, location):
    weather_data = get_weather_info(location)
    if weather_data:
        essential_data = {
            "location": weather_data.get("name"),
            "temperature": weather_data["main"].get("temp"),
            "description": weather_data["weather"][0].get("description"),
            "humidity": weather_data["main"].get("humidity"),
            "wind_speed": weather_data["wind"].get("speed"),
            "country": weather_data["sys"].get("country"),
        }
        return Response(essential_data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Failed to fetch weather data"}, status=status.HTTP_400_BAD_REQUEST)