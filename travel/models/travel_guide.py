from django.db import models
from django.contrib.auth import get_user_model
from travel.utils.weather_utils import get_weather_info

User = get_user_model()

class TravelGuide(models.Model):
    GUIDE_TYPES = [
        ('cultural', 'Cultural Guide'),
        ('practical', 'Practical Guide'),
        ('safety', 'Safety Guide'),
        ('language', 'Language Guide'),
        ('transport', 'Transport Guide'),
        ('food', 'Food Guide'),
        ('shopping', 'Shopping Guide'),
        ('emergency', 'Emergency Guide'),
    ]

    REGION_CHOICES = [
        ('addis', 'Addis Ababa'),
        ('oromia', 'Oromia'),
        ('amhara', 'Amhara'),
        ('snnpr', 'SNNPR'),
        ('tigray', 'Tigray'),
        ('somali', 'Somali'),
        ('afar', 'Afar'),
        ('benishangul', 'Benishangul-Gumuz'),
        ('gambela', 'Gambela'),
        ('harari', 'Harari'),
        ('dire_dawa', 'Dire Dawa'),
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    guide_type = models.CharField(max_length=20, choices=GUIDE_TYPES)
    region = models.CharField(max_length=20, choices=REGION_CHOICES)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='guides')
    
    # Content
    content = models.TextField()
    summary = models.TextField()
    key_points = models.JSONField(default=list)
    images = models.JSONField(default=list)
    videos = models.JSONField(default=list)
    
    # Cultural Information
    customs = models.JSONField(default=list)
    etiquette = models.JSONField(default=list)
    festivals = models.JSONField(default=list)
    traditions = models.JSONField(default=list)
    
    # Practical Information
    transportation = models.JSONField(default=dict)
    accommodation = models.JSONField(default=dict)
    food_and_drink = models.JSONField(default=dict)
    shopping = models.JSONField(default=dict)
    
    # Safety Information
    safety_tips = models.JSONField(default=list)
    emergency_contacts = models.JSONField(default=list)
    health_advisories = models.JSONField(default=list)
    weather_info = models.JSONField(default=dict)  # Implemented weather_info field
    
    # Language Information
    common_phrases = models.JSONField(default=list)
    pronunciation_guide = models.JSONField(default=dict)
    language_tips = models.TextField(blank=True)
    
    # Interactive Features
    interactive_map = models.JSONField(default=dict)
    offline_content = models.JSONField(default=dict)
    related_guides = models.ManyToManyField('self', blank=True)
    
    # Metadata
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['guide_type']),
            models.Index(fields=['region']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_guide_type_display()})"

    def increment_views(self):
        """Increment the view count"""
        self.views_count += 1
        self.save()

    def get_related_content(self):
        """Get related guides and content"""
        return {
            'related_guides': self.related_guides.all(),
            'interactive_map': self.interactive_map,
            'offline_content': self.offline_content,
        }

    def get_safety_info(self):
        """Get comprehensive safety information"""
        return {
            'safety_tips': self.safety_tips,
            'emergency_contacts': self.emergency_contacts,
            'health_advisories': self.health_advisories,
            'weather_info': self.weather_info,  # Connected weather_info
        }

    def get_cultural_info(self):
        """Get cultural information"""
        return {
            'customs': self.customs,
            'etiquette': self.etiquette,
            'festivals': self.festivals,
            'traditions': self.traditions,
        }

    def get_practical_info(self):
        """Get practical information"""
        return {
            'transportation': self.transportation,
            'accommodation': self.accommodation,
            'food_and_drink': self.food_and_drink,
            'shopping': self.shopping,
        }

    def get_language_info(self):
        """Get language-related information"""
        return {
            'common_phrases': self.common_phrases,
            'pronunciation_guide': self.pronunciation_guide,
            'language_tips': self.language_tips,
        }

    def update_weather_info(self):
        """Update weather information for the travel guide"""
        weather_data = get_weather_info(self.region)
        if weather_data:
            self.weather_info = weather_data
            self.save()