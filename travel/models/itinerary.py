from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Itinerary(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    TRIP_TYPE_CHOICES = [
        ('solo', 'Solo'),
        ('couple', 'Couple'),
        ('family', 'Family'),
        ('friends', 'Friends'),
        ('business', 'Business'),
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='itineraries')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Trip Details
    start_date = models.DateField()
    end_date = models.DateField()
    trip_type = models.CharField(max_length=20, choices=TRIP_TYPE_CHOICES)
    number_of_travelers = models.PositiveIntegerField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    preferences = models.JSONField(default=dict)  # Store user preferences
    
    # Destinations and Activities
    destinations = models.JSONField(default=list)  # List of destinations with details
    activities = models.JSONField(default=list)    # List of planned activities
    accommodations = models.JSONField(default=list) # List of accommodations
    transportation = models.JSONField(default=list) # Transportation details
    
    # AI-Generated Content
    ai_recommendations = models.JSONField(default=list)  # AI-generated recommendations
    cultural_notes = models.JSONField(default=list)      # Cultural information
    weather_info = models.JSONField(default=dict)        # Weather forecasts
    safety_tips = models.JSONField(default=list)         # Safety information
    
    # Booking and Costs
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bookings = models.JSONField(default=list)  # Track all bookings
    payment_status = models.JSONField(default=dict)  # Track payment status
    
    # Emergency Information
    emergency_contacts = models.JSONField(default=list)
    medical_info = models.TextField(blank=True)
    insurance_info = models.JSONField(default=dict)
    
    # Sharing and Collaboration
    is_public = models.BooleanField(default=False)
    shared_with = models.JSONField(default=list)  # List of users with access
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_generated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['start_date']),
            models.Index(fields=['status']),
        ]
        verbose_name_plural = "itineraries"

    def __str__(self):
        return f"{self.title} ({self.start_date} to {self.end_date})"

    def calculate_total_cost(self):
        """Calculate the total cost of the itinerary"""
        total = 0
        # Add accommodation costs
        for accommodation in self.accommodations:
            total += float(accommodation.get('cost', 0))
        # Add transportation costs
        for transport in self.transportation:
            total += float(transport.get('cost', 0))
        # Add activity costs
        for activity in self.activities:
            total += float(activity.get('cost', 0))
        
        self.total_cost = total
        self.save()
        return total

    def get_duration(self):
        """Calculate the duration of the trip in days"""
        return (self.end_date - self.start_date).days + 1

    def is_active(self):
        """Check if the itinerary is currently active"""
        from django.utils import timezone
        current_date = timezone.now().date()
        return (
            self.status == 'active' and 
            self.start_date <= current_date <= self.end_date
        )

    def can_be_edited(self):
        """Check if the itinerary can still be edited"""
        from django.utils import timezone
        return self.start_date > timezone.now().date()

    def share_with_user(self, user_email):
        """Share the itinerary with another user"""
        if user_email not in self.shared_with:
            self.shared_with.append(user_email)
            self.save()

    def update_weather_info(self):
        """Update weather information for the itinerary dates"""
        # This would be implemented to fetch weather data from an API
        pass