from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from uuid import UUID
from .serializers import UserSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    EmailVerificationSerializer,
    LoginSerializer,
    TokenRefreshSerializer,
    LogoutSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            token = user.generate_email_verification_token()

            verification_url = f"{request.scheme}://{request.get_host()}/auth/verify-email/?token={token}"
            send_mail(
                'Verify your email',
                f'Please click the link to verify your email: {verification_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            user_data = UserSerializer(user).data
            return Response(user_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                token = UUID(serializer.validated_data['token'])
                user = User.objects.filter(email_verification_token=token).first()

                if not user:
                    return Response(
                        {'detail': 'Invalid verification token.', 'code': 'invalid_token'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                user.is_verified = True
                user.email_verification_token = None
                user.save()

                return Response({'detail': 'Email verified successfully.'}, status=status.HTTP_200_OK)
            except ValueError:
                return Response(
                    {'detail': 'Invalid token format.', 'code': 'invalid_token_format'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = User.objects.filter(email=email).first()

            if user is None or not user.check_password(password):
                return Response(
                    {'detail': 'Invalid credentials.', 'code': 'invalid_credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            tokens = get_tokens_for_user(user)
            user_data = UserSerializer(user).data

            response_data = {
                'access': tokens['access'],
                'refresh': tokens['refresh'],
                'user': user_data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        if serializer.is_valid():
            try:
                refresh_token = serializer.validated_data['refresh']
                token = RefreshToken(refresh_token)

                return Response({
                    'access': str(token.access_token)
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {'detail': 'Invalid refresh token.', 'code': 'invalid_token'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            try:
                refresh_token = serializer.validated_data['refresh']
                token = RefreshToken(refresh_token)
                token.blacklist()

                return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {'detail': 'Invalid token.', 'code': 'invalid_token'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()

            if user:
                token = user.generate_password_reset_token()

                reset_url = f"{request.scheme}://{request.get_host()}/auth/password-reset/confirm/?token={token}"
                send_mail(
                    'Reset your password',
                    f'Please click the link to reset your password: {reset_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

            return Response({'detail': 'Password reset email sent.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                token = UUID(serializer.validated_data['token'])
                password = serializer.validated_data['password']

                user = User.objects.filter(password_reset_token=token).first()

                if not user:
                    return Response(
                        {'detail': 'Invalid reset token.', 'code': 'invalid_token'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                token_age = timezone.now() - user.password_reset_token_created_at
                if token_age > timedelta(hours=24):
                    return Response(
                        {'detail': 'Token has expired.', 'code': 'token_expired'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                user.set_password(password)
                user.password_reset_token = None
                user.password_reset_token_created_at = None
                user.save()

                return Response({'detail': 'Password reset successful.'}, status=status.HTTP_200_OK)
            except ValueError:
                return Response(
                    {'detail': 'Invalid token format.', 'code': 'invalid_token_format'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.role == 'admin':
            return User.objects.all().order_by('id')
        return User.objects.filter(id=self.request.user.id)
