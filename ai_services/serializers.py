from rest_framework import serializers
from .models import TravelPlan, AIRecommendation, TravelAssistant, UserPreference, SentimentAnalysis
from users.serializers import UserSerializer
from travel.serializers import DestinationSerializer
from travel.serializers import ReviewSerializer

class TravelPlanSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    destination = DestinationSerializer(read_only=True)

    class Meta:
        model = TravelPlan
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'user')

class TravelPlanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelPlan
        fields = ('destination', 'start_date', 'end_date', 'preferences')

class AIRecommendationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AIRecommendation
        fields = '__all__'
        read_only_fields = ('created_at', 'user')

class AIRecommendationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIRecommendation
        fields = ('recommendation_type',)

class TravelAssistantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = TravelAssistant
        fields = '__all__'
        read_only_fields = ('created_at', 'user')

class TravelAssistantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelAssistant
        fields = ('question',)

class UserPreferenceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserPreference
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'user')

class SentimentAnalysisSerializer(serializers.ModelSerializer):
    review = ReviewSerializer(read_only=True)

    class Meta:
        model = SentimentAnalysis
        fields = '__all__'
        read_only_fields = ('created_at',)