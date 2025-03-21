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
from travel.views.map_view import get_directions, download_map, nearby_attractions
from users.views import UserRegistrationView, UserLoginView, UserLogoutView, PasswordResetView, ForgotPasswordView, VerifyResetCodeView, PasswordResetConfirmView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('profile/', user_profile, name='user-profile'),
    path('itineraries/', itinerary_list, name='itinerary-list'),
    path('itineraries/<int:id>/', itinerary_detail, name='itinerary-detail'),
    path('itineraries/<int:id>/share/', share_itinerary, name='share-itinerary'),
    path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', UserLoginView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', UserLogoutView.as_view(), name='user-logout'),
    path('auth/password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('auth/verify-reset-code/', VerifyResetCodeView.as_view(), name='verify-reset-code'),
    path('auth/reset-password-confirm/', PasswordResetConfirmView.as_view(), name='reset-password-confirm'),
    path('map/directions/', get_directions, name='get-directions'),
    path('map/download/', download_map, name='download-map'),
    path('map/nearby/', nearby_attractions, name='nearby-attractions'),
]