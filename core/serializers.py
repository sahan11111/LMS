from rest_framework import serializers
from . import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from random import randint
from django.db import transaction
from django.contrib.auth.hashers import make_password

User = get_user_model()
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
        role = validated_data.get('role')

        # Create user
        user = models.User.objects.create_user(**validated_data)
        user.role = role
        # yesle chai user lai active huna dina hunna. 
        # By default user chai 'is_active=True' hunxa
        user.is_active = False
        
        # OTP ta random integer hunxa ni tye vayera 'randint' use gareko. 
        # Hamle 'OTP=charfield' garaxam so 'str' use gareko
        user.otp = str(randint(0000,9999))
        user.save()            
            
        # mail send garda yo chai lekhnai parxa    
        send_mail(
            subject='User activation',
            message=f'Your OTP is {user.otp} for {user.email}',
            from_email=settings.SENDER_EMAIL_USER,
            recipient_list=[user.email],
            fail_silently=False
        )
        

        # Assign user to the corresponding group
        group, _ = Group.objects.get_or_create(name=role.capitalize())
        user.groups.add(group)

        return user
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=models.User.ROLE_CHOICES)

# This is for User Verification   
class UserVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255)
    
    def update(self, user, validated_data):
        otp = validated_data.get('otp')
        email = validated_data.get('email')
        
        if otp == user.otp and email == user.email:
            user.is_active = True
            user.otp = None
            user.save()
        else:
            raise serializers.ValidationError({
                'otp': 'Invalid otp or email'
            })

        return user
    
# This is for Forget Password
class UserForgetPasswordSeralizer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value
    
    
#This is for updating forget password

class UpadteUserForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs.get('password')!= attrs.get('confirm_password'):
            raise serializers.ValidationError({
                'confirm_password' : 'Password do not match'
            })
        return super().validate(attrs)
    
    def update(self, user, validated_data):
        otp=validated_data.get('otp')
        email=validated_data.get('email')
        if otp==user.otp and email==user.email:
            # make_password rakhena vani validation ma error aauxa ra hamle manager banauda password hash ma store hunxa so hash ma ja rakhna parxa otherwise error aauxa login garda
            user.password=make_password(validated_data.get('password'))
            
            # 'OTP=none' le chai ekchoti pathako OTP, ekchoti matra use garna milxa
            user.otp=None
            user.save()
        else:
            raise serializers.ValidationError({
                'otp': 'Invalid otp or email'
            })
        return super().update(user, validated_data)