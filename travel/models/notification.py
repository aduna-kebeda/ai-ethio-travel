from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('booking', 'Booking Update'),
        ('itinerary', 'Itinerary Update'),
        ('weather', 'Weather Alert'),
        ('safety', 'Safety Alert'),
        ('news', 'News Update'),
        ('event', 'Event Reminder'),
        ('recommendation', 'Travel Recommendation'),
        ('emergency', 'Emergency Alert'),
        ('system', 'System Notification'),
    ]

    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    # Basic Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Content and Links
    content = models.JSONField(default=dict)  # Store additional notification data
    link = models.URLField(blank=True)  # URL to related content
    related_object = models.JSONField(default=dict)  # Store related object reference
    
    # Delivery Status
    is_read = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    delivery_attempts = models.PositiveIntegerField(default=0)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Scheduling
    scheduled_for = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['is_read']),
            models.Index(fields=['scheduled_for']),
        ]

    def __str__(self):
        return f"{self.notification_type}: {self.title}"

    def mark_as_read(self):
        """Mark the notification as read"""
        self.is_read = True
        self.save()

    def mark_as_delivered(self):
        """Mark the notification as delivered"""
        self.is_delivered = True
        self.delivered_at = timezone.now()
        self.save()

    def increment_delivery_attempts(self):
        """Increment delivery attempts counter"""
        self.delivery_attempts += 1
        self.save()

    def is_expired(self):
        """Check if the notification has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def should_deliver(self):
        """Check if the notification should be delivered"""
        if self.scheduled_for:
            return timezone.now() >= self.scheduled_for
        return True

    def get_notification_data(self):
        """Get formatted notification data for delivery"""
        return {
            'id': self.id,
            'type': self.notification_type,
            'priority': self.priority,
            'title': self.title,
            'message': self.message,
            'content': self.content,
            'link': self.link,
            'created_at': self.created_at.isoformat(),
        } 