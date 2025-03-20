from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class News(models.Model):
    NEWS_TYPES = [
        ('tourism', 'Tourism News'),
        ('safety', 'Safety Advisory'),
        ('event', 'Event Update'),
        ('promotion', 'Promotion'),
        ('announcement', 'Announcement'),
        ('weather', 'Weather Update'),
        ('emergency', 'Emergency Alert'),
        ('feature', 'Feature Story'),
    ]

    REGION_CHOICES = [
        ('addis', 'Addis Ababa'),
        ('amhara', 'Amhara'),
        ('oromia', 'Oromia'),
        ('snnpr', 'SNNPR'),
        ('tigray', 'Tigray'),
        ('somali', 'Somali'),
        ('afar', 'Afar'),
        ('benishangul', 'Benishangul-Gumuz'),
        ('gambela', 'Gambela'),
        ('harari', 'Harari'),
        ('dire_dawa', 'Dire Dawa'),
        ('national', 'National'),
        ('international', 'International'),
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    news_type = models.CharField(max_length=20, choices=NEWS_TYPES)
    region = models.CharField(max_length=20, choices=REGION_CHOICES)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='news')
    
    # Content
    content = models.TextField()
    summary = models.TextField()
    images = models.JSONField(default=list)
    videos = models.JSONField(default=list)
    links = models.JSONField(default=list)
    
    # Related Information
    related_destinations = models.JSONField(default=list)
    related_events = models.JSONField(default=list)
    related_businesses = models.JSONField(default=list)
    tags = models.JSONField(default=list)
    
    # Impact and Priority
    impact_level = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ])
    requires_action = models.BooleanField(default=False)
    action_required = models.TextField(blank=True)
    
    # Validity and Timing
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)
    is_time_sensitive = models.BooleanField(default=False)
    
    # Distribution
    target_audience = models.JSONField(default=list)
    notification_sent = models.BooleanField(default=False)
    notification_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Engagement
    views_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['news_type']),
            models.Index(fields=['region']),
            models.Index(fields=['valid_from']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
        ]
        verbose_name_plural = "news"

    def __str__(self):
        return f"{self.title} ({self.get_news_type_display()})"

    def increment_views(self):
        """Increment the view count"""
        self.views_count += 1
        self.save()

    def increment_shares(self):
        """Increment the shares count"""
        self.shares_count += 1
        self.save()

    def increment_comments(self):
        """Increment the comments count"""
        self.comments_count += 1
        self.save()

    def is_valid(self):
        """Check if the news is currently valid"""
        from django.utils import timezone
        current_time = timezone.now()
        
        if self.valid_until:
            return self.valid_from <= current_time <= self.valid_until
        return self.valid_from <= current_time

    def mark_notification_sent(self):
        """Mark that notification has been sent"""
        from django.utils import timezone
        self.notification_sent = True
        self.notification_sent_at = timezone.now()
        self.save()

    def get_related_content(self):
        """Get related content information"""
        return {
            'destinations': self.related_destinations,
            'events': self.related_events,
            'businesses': self.related_businesses,
            'tags': self.tags,
        }

    def get_engagement_stats(self):
        """Get engagement statistics"""
        return {
            'views': self.views_count,
            'shares': self.shares_count,
            'comments': self.comments_count,
        }

    def get_notification_data(self):
        """Get data for notification"""
        return {
            'title': self.title,
            'summary': self.summary,
            'type': self.news_type,
            'impact_level': self.impact_level,
            'requires_action': self.requires_action,
            'action_required': self.action_required,
            'valid_from': self.valid_from.isoformat(),
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
        } 