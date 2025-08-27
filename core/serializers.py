from rest_framework import serializers
from . import models

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=models.User.ROLE_CHOICES)

    class Meta:
        model = models.User
        fields = ['username', 'password', 'confirm_password', 'email', 'role']

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match'
            })
        return attrs

    def create(self, validated_data):
        # remove confirm_password before creating user
        validated_data.pop('confirm_password')
        user = models.User.objects.create_user(**validated_data)
        return user
    
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=models.User.ROLE_CHOICES)

