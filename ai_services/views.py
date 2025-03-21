import os
import requests
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.conf import settings
from .models import TravelPlan, AIRecommendation, TravelAssistant, UserPreference
from ai_services.serializers import (
    TravelPlanSerializer, TravelPlanCreateSerializer,
    AIRecommendationSerializer, AIRecommendationCreateSerializer,
    TravelAssistantSerializer, TravelAssistantCreateSerializer,
    UserPreferenceSerializer
)
from travel.utils.weather_utils import get_weather_info
from .utils.ai_utils import get_gemini_recommendations
from .utils.real_time_updates import get_weather_updates, get_airport_schedule
import logging

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Load Gemini API configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or settings.GEMINI_API_KEY
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

class TravelPlanViewSet(viewsets.ModelViewSet):
    serializer_class = TravelPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TravelPlan.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return TravelPlanCreateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        preferences = serializer.validated_data['preferences']
        destination = serializer.validated_data['destination']
        
        user_preferences = UserPreference.objects.filter(user=self.request.user).first()
        if user_preferences:
            preferences.update(user_preferences.interests)
        
        prompt = f"""Create a detailed travel plan for {destination.name} with the following preferences:
        - Duration: {serializer.validated_data['start_date']} to {serializer.validated_data['end_date']}
        - Preferences: {preferences}
        - Cultural considerations: {destination.cultural_notes}
        - Safety information: {destination.safety_notes}
        
        Please include:
        1. Daily itinerary
        2. Recommended activities
        3. Cultural experiences
        4. Safety tips
        5. Local customs to be aware of"""
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            generated_text = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            generated_plan = {'itinerary': generated_text, 'preferences': preferences}
            serializer.save(user=self.request.user, generated_plan=generated_plan)
        else:
            logger.error(f"Error generating travel plan: {response.status_code} - {response.text}")
            raise Exception("Failed to generate travel plan")

class AIRecommendationViewSet(viewsets.ModelViewSet):
    serializer_class = AIRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AIRecommendation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return AIRecommendationCreateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        recommendation_type = serializer.validated_data['recommendation_type']
        
        user_preferences = UserPreference.objects.filter(user=self.request.user).first()
        preferences = user_preferences.interests if user_preferences else {}
        
        prompt = f"""Based on the user's preferences: {preferences}
        Provide personalized {recommendation_type} recommendations for Ethiopia.
        Include:
        1. Top recommendations
        2. Why these match the user's interests
        3. Cultural context
        4. Safety considerations"""
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            recommendations_text = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            recommendations = {'type': recommendation_type, 'recommendations': recommendations_text}
            serializer.save(user=self.request.user, recommendations=recommendations)
        else:
            logger.error(f"Error generating recommendations: {response.status_code} - {response.text}")
            raise Exception("Failed to generate recommendations")

class TravelAssistantViewSet(viewsets.ModelViewSet):
    serializer_class = TravelAssistantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TravelAssistant.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return TravelAssistantCreateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        question = serializer.validated_data['question']
        
        prompt = f"""As an Ethiopian travel assistant, answer this question: {question}
        Please provide:
        1. Accurate and up-to-date information
        2. Cultural context where relevant
        3. Safety considerations
        4. Practical tips"""
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            response_text = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            serializer.save(user=self.request.user, response=response_text)
        else:
            logger.error(f"Error generating assistant response: {response.status_code} - {response.text}")
            raise Exception("Failed to generate assistant response")

class UserPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def update_preferences(self, request, pk=None):
        user_preference = self.get_object()
        serializer = self.get_serializer(user_preference, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def generate_recommendations(request):
    try:
        user_preferences = request.data
        logger.info(f"Received user preferences: {user_preferences}")
        
        if not isinstance(user_preferences, dict) or 'interests' not in user_preferences:
            logger.error("Invalid input: 'interests' field is required")
            return Response(
                {"error": "Invalid input: 'interests' field is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recommendations = get_gemini_recommendations(user_preferences)
        if recommendations:
            return Response(recommendations, status=status.HTTP_200_OK)
        else:
            logger.error("Failed to generate recommendations")
            return Response(
                {"error": "Failed to generate recommendations"},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        logger.error(f"Error in generate_recommendations: {str(e)}")
        return Response(
            {"error": f"Internal server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def fetch_weather(request, location):
    weather_data = get_weather_updates(location)
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

@api_view(['GET'])
def fetch_airport_schedule(request, airport_code):
    schedule_data = get_airport_schedule(airport_code)
    if schedule_data:
        return Response(schedule_data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Failed to fetch airport schedule data"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def ai_chatbot(request):
    try:
        user_message = request.data.get('message', '')
        logger.info(f"Received message from user: {user_message}")
        
        prompt = f"""User: {user_message}\nAI:"""
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        logger.info(f"Request to Gemini API: {response.request.body}")
        
        if response.status_code == 200:
            response_data = response.json()
            logger.info(f"Full response from Gemini API: {response_data}")
            ai_response = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
            logger.info(f"AI response: {ai_response}")
            return Response({'response': ai_response}, status=status.HTTP_200_OK)
        else:
            logger.error(f"Error fetching AI response: {response.status_code} - {response.text}")
            return Response({'error': "Failed to fetch AI response"}, status=response.status_code)
    except Exception as e:
        logger.error(f"Error in AI chatbot: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)