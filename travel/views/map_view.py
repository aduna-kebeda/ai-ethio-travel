from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import openrouteservice
import logging
from django.conf import settings
from django.shortcuts import render

logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_directions(request):
    """
    API endpoint to get directions between two locations using OpenRouteService.
    
    Query Parameters:
        - start (str): Starting location (e.g., "Addis Ababa").
        - end (str): Destination location (e.g., "Gondar").
        - profile (str, optional): Travel mode (e.g., "driving-car", "foot-walking"). Default: "driving-car".
    
    Returns:
        - distance_km (float): Distance in kilometers.
        - duration_minutes (float): Duration in minutes.
        - map_link (str): Google Maps URL for the route (optional, without API key).
        - route (dict): Full GeoJSON route data.
    """
    client = openrouteservice.Client(key=settings.ORS_API_KEY)
    start = request.query_params.get('start')
    end = request.query_params.get('end')
    profile = request.query_params.get('profile', 'driving-car')  # Default: driving-car

    if not start or not end:
        logger.error("Start and end parameters are required")
        return Response({"error": "Start and end parameters are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Geocode start location
        start_coords = geocode_location(client, start)
        if not start_coords:
            logger.error(f"Could not geocode start location: {start}")
            return Response({"error": f"Could not geocode start location: {start}"}, status=status.HTTP_400_BAD_REQUEST)

        # Geocode end location
        end_coords = geocode_location(client, end)
        if not end_coords:
            logger.error(f"Could not geocode end location: {end}")
            return Response({"error": f"Could not geocode end location: {end}"}, status=status.HTTP_400_BAD_REQUEST)

        # Get directions
        directions = client.directions(
            coordinates=[start_coords, end_coords],
            profile=profile,
            format='geojson'
        )
        distance_km = directions['features'][0]['properties']['segments'][0]['distance'] / 1000  # Meters to kilometers
        duration_sec = directions['features'][0]['properties']['segments'][0]['duration']  # Duration in seconds

        # Google Maps link (no API key needed)
        map_link = f"https://www.google.com/maps/dir/?api=1&origin={start}&destination={end}&travelmode={profile.split('-')[0]}"

        response_data = {
            "distance_km": round(distance_km, 2),
            "duration_minutes": round(duration_sec / 60, 2),
            "map_link": map_link,
            "route": directions  # Full GeoJSON for detailed route info
        }

        logger.info(f"Directions generated: {start} to {end}, Distance: {distance_km} km")
        return Response(response_data, status=status.HTTP_200_OK)

    except openrouteservice.exceptions.ApiError as e:
        logger.error(f"OpenRouteService API error: {e}")
        return Response({"error": f"OpenRouteService API error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error in get_directions: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def download_map(request):
    """
    API endpoint to generate and provide a GeoJSON map for a given location and area using OpenRouteService.
    
    Query Parameters:
        - location (str): The name of the location (e.g., "Addis Ababa").
        - area (float): The radius of the area in kilometers (e.g., "5" for 5 km). Must be a positive number.
    
    Returns:
        - geojson (dict): GeoJSON data representing the area (isochrone).
        - center (list): Coordinates of the location [longitude, latitude].
        - area_km (float): The requested area in kilometers.
    
    Example:
        GET /map/download/?location=Addis%20Ababa&area=5
    """
    try:
        location = request.query_params.get('location')
        area_km = request.query_params.get('area')

        if not location or not area_km:
            logger.error("Location and area parameters are required")
            return Response(
                {"error": "Location and area parameters are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate and convert area to float
        try:
            area_km = float(area_km)
            if area_km <= 0:
                logger.error(f"Area must be a positive number, got: {area_km}")
                return Response(
                    {"error": "Area must be a positive number (kilometers)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            logger.error(f"Invalid area value: {area_km}")
            return Response(
                {"error": "Area must be a valid number (kilometers)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        client = openrouteservice.Client(key=settings.ORS_API_KEY)

        # Geocode location
        coords = geocode_location(client, location)
        if not coords:
            logger.error(f"Could not geocode location: {location}")
            return Response(
                {"error": f"Could not geocode location: {location}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate map data
        map_data = generate_map(client, coords, area_km)

        if "error" in map_data:
            logger.error(f"Failed to generate map: {map_data['error']}")
            return Response(
                {"error": map_data["error"]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        logger.info(f"Map generated for {location} with {area_km} km area")
        return Response(map_data, status=status.HTTP_200_OK)

    except openrouteservice.exceptions.ApiError as e:
        logger.error(f"OpenRouteService API error: {e}")
        return Response(
            {"error": f"OpenRouteService API error: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f"Error in download_map: {str(e)}")
        return Response(
            {"error": f"Internal server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def nearby_attractions(request):
    """
    API endpoint to find nearby attractions using OpenRouteService POI service.
    
    Query Parameters:
        - location (str): The name of the location (e.g., "Axum").
        - radius (int, optional): Search radius in meters (e.g., "2000"). Default: 1000.
    
    Returns:
        - attractions (list): List of nearby attractions with name, distance, and coordinates.
    """
    client = openrouteservice.Client(key=settings.ORS_API_KEY)
    location = request.query_params.get('location')
    radius = request.query_params.get('radius', 1000)  # Default radius in meters

    if not location:
        logger.error("Location parameter is required")
        return Response({"error": "Location parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        radius = int(radius)  # Ensure radius is an integer
        coords = geocode_location(client, location)
        if not coords:
            logger.error(f"Could not geocode location: {location}")
            return Response({"error": f"Could not geocode location: {location}"}, status=status.HTTP_400_BAD_REQUEST)

        # Corrected params structure for ORS places endpoint
        params = {
            'request': 'pois',
            'geojson': {
                'type': 'Point',
                'coordinates': coords
            },
            'buffer': radius,  # Buffer in meters
            'filters': {
                'category_ids': [206, 208, 220]  # Tourist attractions, museums, historical sites
            },
            'sortby': 'distance'
        }
        logger.debug(f"POI request params: {params}")
        places = client.places(**params)

        # Simplify response
        attractions = [
            {
                "name": feature.get('properties', {}).get('name', 'Unnamed'),
                "distance_m": feature.get('properties', {}).get('distance', 0),
                "coordinates": feature['geometry']['coordinates']
            }
            for feature in places.get('features', [])
        ]

        logger.info(f"Found {len(attractions)} attractions near {location}")
        return Response({"attractions": attractions}, status=status.HTTP_200_OK)

    except openrouteservice.exceptions.ApiError as e:
        logger.error(f"OpenRouteService API error: {e}")
        return Response({"error": f"OpenRouteService API error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error in nearby_attractions: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def geocode_location(client, location):
    """
    Geocode a location name to coordinates using OpenRouteService.
    
    Args:
        client: OpenRouteService client instance.
        location (str): Location name or address.
    
    Returns:
        list: [longitude, latitude] or None if geocoding fails.
    """
    try:
        geocode = client.pelias_search(text=location)
        if geocode and 'features' in geocode and len(geocode['features']) > 0:
            coords = geocode['features'][0]['geometry']['coordinates']
            return [coords[0], coords[1]]  # [longitude, latitude]
    except Exception as e:
        logger.error(f"Geocoding error for {location}: {e}")
    return None

def generate_map(client, coords, area_km):
    """
    Generate a map for the given location and area using OpenRouteService.
    
    Args:
        client: OpenRouteService client instance.
        coords (list): [longitude, latitude] of the center.
        area_km (float): Area radius in kilometers.
    
    Returns:
        dict: Map data including GeoJSON isochrone.
    """
    try:
        # Convert area from kilometers to meters for ORS
        area_m = area_km * 1000

        # Generate isochrone
        isochrone = client.isochrones(
            locations=[coords],
            range=[area_m],  # Distance in meters
            range_type='distance'
        )

        return {
            "geojson": isochrone,
            "center": coords,
            "area_km": area_km
        }

    except Exception as e:
        logger.error(f"Error generating map: {str(e)}")
        return {"error": str(e)}

def map_view(request):
    """
    Render a map view with directions and nearby attractions URLs.
    
    Query Parameters:
        - start (str, optional): Starting location. Default: "Addis Ababa".
        - end (str, optional): Destination location. Default: "Gondar".
        - location (str, optional): Location for nearby attractions. Default: "Gondar".
        - radius (int, optional): Radius for nearby attractions in meters. Default: 1000.
    """
    start = request.GET.get('start', 'Addis Ababa')
    end = request.GET.get('end', 'Gondar')
    location = request.GET.get('location', 'Gondar')
    radius = request.GET.get('radius', 1000)

    directions_url = f'/map/directions/?start={start}&end={end}'
    nearby_url = f'/map/nearby/?location={location}&radius={radius}'
    download_map_url = f'/map/download/?location={location}&area=5'  # Default 5km area

    context = {
        'directions_url': directions_url,
        'nearby_url': nearby_url,
        'download_map_url': download_map_url,
    }
    return render(request, 'map.html', context)