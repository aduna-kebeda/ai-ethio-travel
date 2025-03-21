from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfile(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('am', 'Amharic'),
        ('or', 'Oromiffa'),
        ('ti', 'Tigrinya'),
        ('so', 'Somali'),
    ]

    CURRENCY_CHOICES = [
        ('ETB', 'Ethiopian Birr'),
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
    ]

    # User Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    preferred_language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    preferred_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='ETB')
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    
    # Travel Preferences
    travel_style = models.JSONField(default=dict)
    interests = models.JSONField(default=list)
    dietary_restrictions = models.JSONField(default=list)
    accessibility_needs = models.JSONField(default=list)
    
    # Notification Settings
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    notification_preferences = models.JSONField(default=dict)
    
    # Travel Statistics
    total_trips = models.PositiveIntegerField(default=0)
    visited_destinations = models.JSONField(default=list)
    favorite_destinations = models.JSONField(default=list)
    travel_bucket_list = models.JSONField(default=list)
    
    # Emergency Information
    emergency_contact = models.JSONField(default=dict)
    medical_info = models.TextField(blank=True)
    insurance_info = models.JSONField(default=dict)
    
    # Social Features
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    social_links = models.JSONField(default=dict)
    
    # AI Preferences
    ai_preferences = models.JSONField(default=dict)
    recommendation_history = models.JSONField(default=list)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(null=True, blank=True)

    # Add reset_code field
    reset_code = models.CharField(max_length=6, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['preferred_language']),
        ]

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def update_travel_stats(self):
        from travel.models.itinerary import Itinerary
        completed_trips = Itinerary.objects.filter(
            user=self.user,
            status='completed'
        ).count()
        self.total_trips = completed_trips
        self.save()

    def add_visited_destination(self, destination_id):
        if destination_id not in self.visited_destinations:
            self.visited_destinations.append(destination_id)
            self.save()

    def add_favorite_destination(self, destination_id):
        if destination_id not in self.favorite_destinations:
            self.favorite_destinations.append(destination_id)
            self.save()

    def update_recommendation_history(self, recommendation):
        self.recommendation_history.append(recommendation)
        if len(self.recommendation_history) > 100:
            self.recommendation_history = self.recommendation_history[-100:]
        self.save()

    def get_travel_summary(self):
        from travel.models.itinerary import Itinerary
        completed_trips = Itinerary.objects.filter(
            user=self.user,
            status='completed'
        )
        
        return {
            'total_trips': completed_trips.count(),
            'total_destinations': len(self.visited_destinations),
            'favorite_destinations': len(self.favorite_destinations),
            'bucket_list': len(self.travel_bucket_list),
        }