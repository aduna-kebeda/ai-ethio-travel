from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
import google.generativeai as genai
from django.conf import settings
from .models import TravelPlan, AIRecommendation, TravelAssistant, UserPreference
from .serializers import (
    TravelPlanSerializer, TravelPlanCreateSerializer,
    AIRecommendationSerializer, AIRecommendationCreateSerializer,
    TravelAssistantSerializer, TravelAssistantCreateSerializer,
    UserPreferenceSerializer
)

# Configure Google AI
genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

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
        # Generate AI travel plan based on user preferences
        preferences = serializer.validated_data['preferences']
        destination = serializer.validated_data['destination']
        
        # Get user preferences for better personalization
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
        
        response = model.generate_content(prompt)
        generated_plan = {
            'itinerary': response.text,
            'preferences': preferences
        }
        
        serializer.save(user=self.request.user, generated_plan=generated_plan)

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
        
        # Get user preferences for better personalization
        user_preferences = UserPreference.objects.filter(user=self.request.user).first()
        preferences = user_preferences.interests if user_preferences else {}
        
        prompt = f"""Based on the user's preferences: {preferences}
        Provide personalized {recommendation_type} recommendations for Ethiopia.
        Include:
        1. Top recommendations
        2. Why these match the user's interests
        3. Cultural context
        4. Safety considerations"""
        
        response = model.generate_content(prompt)
        recommendations = {
            'type': recommendation_type,
            'recommendations': response.text
        }
        
        serializer.save(user=self.request.user, recommendations=recommendations)

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
        
        # Generate response using AI
        prompt = f"""As an Ethiopian travel assistant, answer this question: {question}
        Please provide:
        1. Accurate and up-to-date information
        2. Cultural context where relevant
        3. Safety considerations
        4. Practical tips"""
        
        response = model.generate_content(prompt)
        serializer.save(user=self.request.user, response=response.text)

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