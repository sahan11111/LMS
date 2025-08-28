from rest_framework import serializers
from . import models

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=models.User.ROLE_CHOICES)

    class Meta:
        model = models.User
        fields = ['id', 'username', 'email', 'role', 'password', 'confirm_password']
        extra_kwargs = {'id': {'read_only': True}}

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match'
            })
        return attrs

    def create(self, validated_data):
        # remove confirm_password before creating user
        validated_data.pop('confirm_password')
        role= validated_data.get('role')
        
        # Create the user
        user = models.User.objects.create_user(**validated_data)
        group,created= models.Group.objects.get_or_create(name=role.capitalize())
        user.groups.add(group)
        
        return user
    
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=models.User.ROLE_CHOICES)

