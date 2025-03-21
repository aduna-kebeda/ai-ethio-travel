import random
import string
from rest_framework import viewsets, status, permissions, generics, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import LogoutView
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserProfileSerializer,
    ChangePasswordSerializer, ResetPasswordSerializer, ResetPasswordConfirmSerializer,
    VerifyResetCodeSerializer
)
from travel.serializers import DestinationSerializer
from travel.models.destination import Destination
from travel.models.user_profile import UserProfile

User = get_user_model()

# Social Login Views
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    permission_classes = [AllowAny]

class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    permission_classes = [AllowAny]

# User Login and Logout
class UserLoginView(TokenObtainPairView):
    """Login with email and password to obtain JWT tokens."""
    permission_classes = [AllowAny]

class UserLogoutView(LogoutView):
    """Logout user by blacklisting JWT refresh token."""
    permission_classes = [IsAuthenticated]

# User Registration
class UserRegistrationView(generics.CreateAPIView):
    """Register a new user and send email verification link."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        # Send email verification
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}"
        
        send_mail(
            'Verify Your Email',
            f'Click this link to verify your email: {verification_url}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Registration successful. Please verify your email.'
        }, status=status.HTTP_201_CREATED)

# Email Verification
class VerifyEmailView(APIView):
    """Verify user's email using uid and token."""
    permission_classes = [AllowAny]

    def get(self, request):
        uid = request.query_params.get('uid')
        token = request.query_params.get('token')

        if not uid or not token:
            return Response({"error": "UID and token are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                if not user.is_verified:
                    user.is_verified = True
                    user.save()
                    return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
                return Response({"message": "Email already verified"}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid user or token"}, status=status.HTTP_400_BAD_REQUEST)

# Password Reset Flow (Token-Based)
class PasswordResetView(generics.GenericAPIView):
    """Request a password reset link via email."""
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

            send_mail(
                'Reset Your Password',
                f'Click this link to reset your password: {reset_url}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return Response({'message': 'Password reset email sent.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Password reset email sent if the account exists.'}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(generics.GenericAPIView):
    """Confirm password reset with token and new password."""
    serializer_class = ResetPasswordConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        uid = request.data.get('uid')  # UID must be provided in request body

        if not uid:
            return Response({"error": "UID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password successfully reset"}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid user or token"}, status=status.HTTP_400_BAD_REQUEST)

# Password Reset Flow (Code-Based)
class ForgotPasswordView(generics.GenericAPIView):
    """Request a password reset code via email."""
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            reset_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.reset_code = reset_code
            user_profile.save()

            send_mail(
                'Password Reset Code',
                f'Your password reset code is: {reset_code}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return Response({"message": "Password reset code sent to email"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "Password reset code sent if the account exists"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyResetCodeView(generics.GenericAPIView):
    """Verify reset code and set new password."""
    serializer_class = VerifyResetCodeSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        reset_code = serializer.validated_data['reset_code']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(email=email)
            user_profile = UserProfile.objects.get(user=user)
            if user_profile.reset_code == reset_code:
                user.set_password(new_password)
                user_profile.reset_code = ''  # Clear the reset code after use
                user_profile.save()
                user.save()
                return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid reset code"}, status=status.HTTP_400_BAD_REQUEST)
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            return Response({"error": "User or profile not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# User Management ViewSet
class UserViewSet(viewsets.ModelViewSet):
    """Manage user data, including profile and password changes."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return UserProfileSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user's data."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Change current user's password."""
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if user.check_password(serializer.validated_data['old_password']):
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password successfully changed'}, status=status.HTTP_200_OK)
        return Response({'error': 'Incorrect old password'}, status=status.HTTP_400_BAD_REQUEST)

# Destination and Profile ViewSets
class DestinationViewSet(viewsets.ModelViewSet):
    """Manage travel destinations with filtering and search."""
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['region', 'category']
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['name']
    permission_classes = [IsAuthenticated]

class UserProfileViewSet(viewsets.ModelViewSet):
    """Manage user profiles."""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)