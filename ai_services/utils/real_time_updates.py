import os
import requests
import logging

logger = logging.getLogger(__name__)

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
AIRPORT_API_KEY = os.getenv('AIRPORT_API_KEY')

def get_weather_updates(location):
    """
    Get real-time weather updates for a location.
    
    Args:
        location (str): The location for which to get weather updates.
    
    Returns:
        dict: Weather updates.
    """
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            weather_data = response.json()
            logger.info(f"Weather data for {location}: {weather_data}")
            return weather_data
        else:
            logger.error(f"Error fetching weather data: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        return None

def get_airport_schedule(airport_code):
    """
    Get real-time airport schedule updates.
    
    Args:
        airport_code (str): The airport code for which to get schedule updates.
    
    Returns:
        dict: Airport schedule updates.
    """
    try:
        url = f"https://api.flightstats.com/flex/schedules/rest/v1/json/from/{airport_code}/departing"
        headers = {
            "appId": os.getenv('FLIGHTSTATS_APP_ID'),
            "appKey": AIRPORT_API_KEY
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            schedule_data = response.json()
            logger.info(f"Airport schedule data for {airport_code}: {schedule_data}")
            return schedule_data
        else:
            logger.error(f"Error fetching airport schedule data: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error fetching airport schedule data: {str(e)}")
        return None