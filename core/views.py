from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet 
from . import models, serializers
from django.contrib.auth import get_user_model,authenticate
from rest_framework.authtoken.models import Token
class UserViewSet(GenericViewSet,CreateModelMixin):
    queryset = models.User.objects.all()  # Required for ModelViewSet
    serializer_class = serializers.UserSerializer #Default for registering user

    # Override get_serializer_class to return different serializers based on action login
    def get_serializer_class(self):
        if self.action == 'login':
            return serializers.UserLoginSerializer
        return super().get_serializer_class()


        
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        role = serializer.validated_data.get('role')
        user=authenticate(username=username,password=password)
        if user and user.role == role: 
        # get_or_create le k garxa vanda: if token pailai xa vani get garxa ra yedi xaina vani create garxa. 'create' matra garyo vani tesle harek time create garxa so we use get_or_create
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'token': token.key
            })
        return Response({'error': 'Invalid credentials or role'}, status=400)