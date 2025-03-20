from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Destination(models.Model):
    CATEGORY_CHOICES = [
        ('cultural', 'Cultural'),
        ('historical', 'Historical'),
        ('natural', 'Natural'),
        ('adventure', 'Adventure'),
    ]

    SAFETY_LEVEL_CHOICES = [
        ('high', 'High Safety'),
        ('medium', 'Medium Safety'),
        ('caution', 'Exercise Caution'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    region = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    images = models.JSONField(default=list)  # Store multiple image URLs
    price_range = models.CharField(max_length=50)
    best_time_to_visit = models.CharField(max_length=200)
    weather_info = models.JSONField(default=dict)  # Store weather information
    
    # Cultural Information
    cultural_notes = models.TextField(blank=True)
    local_customs = models.TextField(blank=True)
    language_tips = models.TextField(blank=True)
    etiquette_guidelines = models.TextField(blank=True)

    # Safety Information
    safety_level = models.CharField(max_length=50, choices=SAFETY_LEVEL_CHOICES)
    safety_notes = models.TextField(blank=True)
    emergency_contacts = models.JSONField(default=dict)
    health_guidelines = models.TextField(blank=True)
    travel_advisories = models.TextField(blank=True)

    # Practical Information
    transportation_options = models.JSONField(default=list)
    local_transportation = models.TextField(blank=True)
    currency_info = models.TextField(blank=True)
    visa_requirements = models.TextField(blank=True)

    # Additional Information
    attractions = models.JSONField(default=list)
    activities = models.JSONField(default=list)
    amenities = models.JSONField(default=list)
    accessibility_info = models.TextField(blank=True)
    
    # Ratings and Reviews
    average_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    review_count = models.PositiveIntegerField(default=0)

    # Metadata
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['region']),
            models.Index(fields=['safety_level']),
        ]

    def __str__(self):
        return self.name

    def update_rating(self):
        """Update average rating when new reviews are added"""
        from travel.models.review import Review
        reviews = Review.objects.filter(destination=self)
        if reviews.exists():
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.average_rating = round(avg, 2)
            self.review_count = reviews.count()
            self.save() 