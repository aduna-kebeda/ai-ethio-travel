from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from travel.views.business_view import BusinessViewSet
from travel.views.destination_view import DestinationViewSet
from travel.views.event_view import EventViewSet
from travel.views.news_view import NewsViewSet
from travel.views.travel_guide_view import TravelGuideViewSet
from travel.views.review_view import ReviewViewSet
from travel.views.notification_view import NotificationSettingViewSet
from travel.views.user_feedback_view import UserFeedbackViewSet
from travel.views.travel_history_view import TravelHistoryViewSet
from travel.views.itinerary_view import itinerary_list, itinerary_detail, share_itinerary
from travel.views.profile_view import user_profile
from users.views import UserRegistrationView, UserLoginView, UserLogoutView, PasswordResetView

router = DefaultRouter()
router.register('businesses', BusinessViewSet, basename='business')
router.register('destinations', DestinationViewSet, basename='destination')
router.register('events', EventViewSet, basename='event')
router.register('news', NewsViewSet, basename='news')
router.register('travel-guides', TravelGuideViewSet, basename='travel-guide')
router.register('reviews', ReviewViewSet, basename='review')
router.register('notifications', NotificationSettingViewSet, basename='notification')
router.register('feedback', UserFeedbackViewSet, basename='feedback')
router.register('travel-history', TravelHistoryViewSet, basename='travel-history')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', user_profile, name='user-profile'),
    path('itineraries/', itinerary_list, name='itinerary-list'),
    path('itineraries/<int:id>/', itinerary_detail, name='itinerary-detail'),
    path('itineraries/<int:id>/share/', share_itinerary, name='share-itinerary'),
    path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('auth/logout/', UserLogoutView.as_view(), name='user-logout'),
    path('auth/password-reset/', PasswordResetView.as_view(), name='password-reset'),
]