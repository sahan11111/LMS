from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin,ListModelMixin
from rest_framework.viewsets import GenericViewSet 
from . import models, serializers
from django.contrib.auth import get_user_model,authenticate
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
User = get_user_model()

class UserViewSet(GenericViewSet,CreateModelMixin):
    queryset = models.User.objects.all()  # Required for ModelViewSet
    serializer_class = serializers.UserSerializer #Default for registering user
    
    # This view is for user verification
    @swagger_auto_schema(
        methods=['put'],
        request_body=serializers.UserVerificationSerializer
    )
    @action(methods=['put'],detail=False)
    def verification(self, request):
        user = get_object_or_404(User, email=request.data.get('email'))
        serializer = serializers.UserVerificationSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'details':'User has been successfully verified.'
        })
    def get_permissions(self):
        if self.action in ['create', 'login', 'verification']:
            return [AllowAny()]
        return [IsAuthenticated()]

    # Override get_serializer_class to return different serializers based on action login
    def get_serializer_class(self):
        if self.action == 'login':
            return serializers.UserLoginSerializer
        return super().get_serializer_class()


    @action(detail=False, methods=['get'], url_path='detail', permission_classes=[IsAuthenticated])
    def user_detail(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        role = serializer.validated_data.get('role')

        # ✅ authenticate with email (USERNAME_FIELD)
        user = authenticate(request, email=email, password=password)

        if not user:
            return Response({"error": "Invalid email or password"}, status=400)

        if user.role != role:
            return Response({"error": "Role mismatch"}, status=400)

        if not user.is_active:
            raise PermissionDenied("OTP verification incomplete. Please verify your email to activate the account.")

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "groups": list(user.groups.values_list("name", flat=True)),
            "token": token.key,
        })


    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def list_users(self, request):
        user = request.user
        if not user.groups.filter(name="Admin").exists():
            return Response({'detail': 'You do not have permission to view this.'}, status=403)
        
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)