from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Business(models.Model):
    BUSINESS_TYPES = [
        ('hotel', 'Hotel'),
        ('restaurant', 'Restaurant'),
        ('tour_operator', 'Tour Operator'),
        ('shop', 'Shop'),
        ('transport', 'Transportation'),
        ('guide', 'Tour Guide'),
        ('other', 'Other'),
    ]

    PRICE_RANGES = [
        ('budget', 'Budget'),
        ('mid_range', 'Mid Range'),
        ('luxury', 'Luxury'),
    ]

    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    # Basic Information
    name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=50, choices=BUSINESS_TYPES)
    description = models.TextField()
    price_range = models.CharField(max_length=50, choices=PRICE_RANGES)
    
    # Contact Information
    address = models.TextField()
    location = models.CharField(max_length=200)
    region = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    website = models.URLField(blank=True)
    social_media = models.JSONField(default=dict)  # Store social media links

    # Business Details
    services = models.JSONField(default=list)
    amenities = models.JSONField(default=list)
    images = models.JSONField(default=list)  # Store multiple image URLs
    opening_hours = models.JSONField(default=dict)  # Store opening hours for each day
    payment_methods = models.JSONField(default=list)
    languages_spoken = models.JSONField(default=list)

    # Verification and Status
    is_verified = models.BooleanField(default=False)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verification_notes = models.TextField(blank=True)
    business_license = models.CharField(max_length=100, blank=True)
    
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
            models.Index(fields=['business_type']),
            models.Index(fields=['region']),
            models.Index(fields=['is_verified']),
        ]
        verbose_name_plural = "businesses"

    def __str__(self):
        return f"{self.name} ({self.get_business_type_display()})"

    def update_rating(self):
        """Update average rating when new reviews are added"""
        from travel.models.review import Review
        reviews = Review.objects.filter(business=self)
        if reviews.exists():
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.average_rating = round(avg, 2)
            self.review_count = reviews.count()
            self.save()

    def get_reviews(self):
        """Get all reviews for this business"""
        from travel.models.review import Review
        return Review.objects.filter(business=self).order_by('-created_at') 