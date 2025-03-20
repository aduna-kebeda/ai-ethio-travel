from rest_framework import serializers
from .models.user_profile import UserProfile
from .models.business import Business
from .models.destination import Destination
from .models.event import Event
from .models.news import News
from .models.travel_guide import TravelGuide
from .models.review import Review, ReviewImage, ReviewLike  # Update this import
from .models.itinerary import Itinerary
from .models.user_interaction import UserInteraction
from .models.notification_setting import NotificationSetting
from .models.user_feedback import UserFeedback
from .models.certification_code import CertificationCode
from .models.travel_history import TravelHistory
from users.serializers import UserSerializer  # Import UserSerializer

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'

class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'

class TravelGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelGuide
        fields = '__all__'
        read_only_fields = ('author', 'published_date')

class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ('id', 'image', 'created_at')
        read_only_fields = ('created_at',)

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    destination = DestinationSerializer(read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'user')

    def get_likes_count(self, obj):
        return obj.likes.count()

class ReviewCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False
    )

    class Meta:
        model = Review
        fields = ('destination', 'rating', 'title', 'content', 'images')

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        review = Review.objects.create(**validated_data)
        
        for image_data in images_data:
            ReviewImage.objects.create(review=review, image=image_data)
        
        return review

class ReviewLikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    review = ReviewSerializer(read_only=True)

    class Meta:
        model = ReviewLike
        fields = ('id', 'user', 'review', 'created_at')
        read_only_fields = ('created_at',)

class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('rating', 'title', 'content')

class ItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class UserInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInteraction
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class NotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSetting
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = '__all__'
        read_only_fields = ('user', 'created_at')

class CertificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificationCode
        fields = '__all__'
        read_only_fields = ('user', 'used')

class TravelHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelHistory
        fields = '__all__'
        read_only_fields = ('user', 'created_at')