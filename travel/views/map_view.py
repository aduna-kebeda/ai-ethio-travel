from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import openrouteservice
from django.conf import settings
from django.shortcuts import render

@api_view(['GET'])
def get_directions(request):
    client = openrouteservice.Client(key=settings.ORS_API_KEY)
    start = request.query_params.get('start')
    end = request.query_params.get('end')
    profile = request.query_params.get('profile', 'driving-car')  # Default profile is driving-car

    if not start or not end:
        return Response({"error": "Start and end parameters are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Geocode start location if it's a place name
        start_coords = geocode_location(client, start)
        if not start_coords:
            return Response({"error": f"Could not geocode start location: {start}"}, status=status.HTTP_400_BAD_REQUEST)

        # Geocode end location if it's a place name
        end_coords = geocode_location(client, end)
        if not end_coords:
            return Response({"error": f"Could not geocode end location: {end}"}, status=status.HTTP_400_BAD_REQUEST)

        directions = client.directions(coordinates=[start_coords, end_coords], profile=profile, format='geojson')
        distance_km = directions['features'][0]['properties']['segments'][0]['distance'] / 1000  # Convert meters to kilometers

        # Use Google Maps for the map link
        map_link = f"https://www.google.com/maps/dir/?api=1&origin={start}&destination={end}"

        response_data = {
            "distance_km": distance_km,
            "map_link": map_link
        }

        return Response(response_data, status=status.HTTP_200_OK)
    except openrouteservice.exceptions.ApiError as e:
        return Response({"error": f"OpenRouteService API error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def geocode_location(client, location):
    try:
        geocode = client.pelias_search(text=location)
        if geocode and 'features' in geocode and len(geocode['features']) > 0:
            coords = geocode['features'][0]['geometry']['coordinates']
            return [coords[0], coords[1]]  # Return [longitude, latitude]
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None

@api_view(['GET'])
def download_map(request):
    # Implementation for downloading offline maps
    area = request.query_params.get('area')

    if not area:
        return Response({"error": "Area parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Simulate map download
    return Response({'message': f'Map for area {area} downloaded successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def nearby_attractions(request):
    client = openrouteservice.Client(key=settings.ORS_API_KEY)
    location = request.query_params.get('location')
    radius = request.query_params.get('radius', 1000)  # Default radius is 1000 meters

    if not location:
        return Response({"error": "Location parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Geocode location if it's a place name
        coords = geocode_location(client, location)
        if not coords:
            return Response({"error": f"Could not geocode location: {location}"}, status=status.HTTP_400_BAD_REQUEST)

        params = {
            'locations': [coords],
            'radius': [radius]
        }
        places = client.places(params)
        return Response(places, status=status.HTTP_200_OK)
    except openrouteservice.exceptions.ApiError as e:
        return Response({"error": f"OpenRouteService API error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def map_view(request):
    start = request.GET.get('start', 'Addis Ababa')
    end = request.GET.get('end', 'Gondar')
    location = request.GET.get('location', 'Gondar')
    radius = request.GET.get('radius', 1000)

    directions_url = f'/map/directions/?start={start}&end={end}'
    nearby_url = f'/map/nearby/?location={location}&radius={radius}'

    context = {
        'directions_url': directions_url,
        'nearby_url': nearby_url,
    }
    return render(request, 'map.html', context)