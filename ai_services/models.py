from django.db import models
from travel.models.review import Review  # Ensure this import is correct
from travel.models.destination import Destination  # Import the Destination model
from django.conf import settings

class TravelPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    preferences = models.JSONField()  # Stores user preferences for the trip
    generated_plan = models.JSONField()  # Stores the AI-generated travel plan
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Travel plan for {self.destination.name} by {self.user.email}"

    class Meta:
        ordering = ['-created_at']

class AIRecommendation(models.Model):
    RECOMMENDATION_TYPES = [
        ('destination', 'Destination'),
        ('activity', 'Activity'),
        ('event', 'Event'),
        ('business', 'Local Business'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recommendation_type = models.CharField(max_length=50, choices=RECOMMENDATION_TYPES)
    recommendations = models.JSONField()  # Stores the AI-generated recommendations
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI recommendation for {self.recommendation_type} by {self.user.email}"

    class Meta:
        ordering = ['-created_at']

class TravelAssistant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Travel assistant conversation with {self.user.email}"

    class Meta:
        ordering = ['-created_at']

class UserPreference(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    interests = models.JSONField()  # Store user interests and preferences
    travel_history = models.JSONField()  # Store user's travel history
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.email}"

    class Meta:
        ordering = ['-updated_at']

class SentimentAnalysis(models.Model):
    review = models.ForeignKey('travel.Review', on_delete=models.CASCADE)  # Update this reference
    sentiment_score = models.FloatField()  # Stores the sentiment score (-1 to 1)
    sentiment_label = models.CharField(max_length=20)  # e.g., 'positive', 'negative', 'neutral'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sentiment analysis for review by {self.review.user.email}"

    class Meta:
        ordering = ['-created_at']