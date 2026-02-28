from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import APIView, action
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.core.mail import send_mail
from drf_yasg.utils import swagger_auto_schema
from . import models, serializers
from .serializers import SuperUserCreateSerializer, generate_otp, OTP_EXPIRY_MINUTES
from rest_framework.generics import CreateAPIView

User = get_user_model()


class UserViewSet(GenericViewSet, CreateModelMixin):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'login', 'verification', 'send_otp_forgot_password', 'update_forgot_password']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'login':
            return serializers.UserLoginSerializer
        return super().get_serializer_class()

    @swagger_auto_schema(methods=['put'], request_body=serializers.UserVerificationSerializer)
    @action(methods=['put'], detail=False)
    def verification(self, request):
        user = get_object_or_404(User, email=request.data.get('email'))
        serializer = serializers.UserVerificationSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'details': 'User has been successfully verified.'})

    @swagger_auto_schema(methods=['post'], request_body=serializers.UserForgotPasswordEmailSerializer)
    @action(methods=['post'], detail=False)
    def send_otp_forgot_password(self, request):
        user = get_object_or_404(User, email=request.data.get('email'))
        serializer = serializers.UserForgotPasswordEmailSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)

        user.otp = generate_otp()
        user.otp_created_at = timezone.now()
        user.save()

        send_mail(
            subject='Forgot Password OTP',
            message=f'Your OTP is {user.otp} for {user.email}. It expires in {OTP_EXPIRY_MINUTES} minutes.',
            from_email=settings.SENDER_EMAIL_USER,
            recipient_list=[user.email],
        )
        return Response({'details': f'OTP has been successfully sent to {user.email}.'})

    @swagger_auto_schema(methods=['put'], request_body=serializers.UpdateUserForgotPasswordEmailSerializer)
    @action(methods=['put'], detail=False)
    def update_forgot_password(self, request):
        user = get_object_or_404(User, email=request.data.get('email'))
        serializer = serializers.UpdateUserForgotPasswordEmailSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'details': f'Password has been successfully updated for {user.email}'})

    @action(detail=False, methods=['get'], url_path='detail', permission_classes=[IsAuthenticated])
    def user_detail(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def list_users(self, request):
        user = request.user
        if not user.is_admin and not user.groups.filter(name='Admin').exists():
            return Response({'detail': 'You do not have permission to view this.'}, status=403)

        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        role = serializer.validated_data.get('role')

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response({'error': 'Invalid email or password'}, status=400)

        if user.role != role:
            return Response({'error': 'Role mismatch'}, status=400)

        if not user.is_active:
            raise PermissionDenied(
                'OTP verification incomplete. Please verify your email to activate the account.'
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'groups': list(user.groups.values_list('name', flat=True)),
            'token': token.key,
        })
        
class SuperUserCreateAPIView(CreateAPIView):
    serializer_class = SuperUserCreateSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Superuser created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)