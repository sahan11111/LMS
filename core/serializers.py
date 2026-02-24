import secrets
from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from . import models

User = get_user_model()

# OTP validity duration in minutes
OTP_EXPIRY_MINUTES = 10


def generate_otp():
    """Generate a cryptographically secure 4-digit OTP."""
    return str(secrets.randbelow(9000) + 1000)  # Always 4 digits: 1000-9999


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
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
        validated_data.pop('confirm_password')
        role = validated_data.get('role')

        user = models.User.objects.create_user(**validated_data)
        user.role = role
        user.is_active = False
        user.otp = generate_otp()
        user.otp_created_at = timezone.now()
        user.save()

        # Send OTP email
        send_mail(
            subject='User Activation - OTP Verification',
            message=f'Your OTP is {user.otp} for {user.email}. It expires in {OTP_EXPIRY_MINUTES} minutes.',
            from_email=settings.SENDER_EMAIL_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )

        # Assign user to the corresponding group
        group, _ = Group.objects.get_or_create(name=role.capitalize())
        user.groups.add(group)

        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=models.User.ROLE_CHOICES)


class UserVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        """Validate OTP and check expiry."""
        return attrs

    def update(self, user, validated_data):
        otp = validated_data.get('otp')
        email = validated_data.get('email')

        if email != user.email:
            raise serializers.ValidationError({'email': 'Email does not match.'})

        if otp != user.otp:
            raise serializers.ValidationError({'otp': 'Invalid OTP.'})

        # Check OTP expiry
        if user.otp_created_at:
            elapsed = (timezone.now() - user.otp_created_at).total_seconds()
            if elapsed > OTP_EXPIRY_MINUTES * 60:
                raise serializers.ValidationError({'otp': 'OTP has expired. Please request a new one.'})

        user.is_active = True
        user.otp = None
        user.otp_created_at = None
        user.save()
        return user


class UserForgotPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class UpdateUserForgotPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match'
            })
        return attrs

    def update(self, user, validated_data):
        otp = validated_data.get('otp')
        email = validated_data.get('email')

        if email != user.email:
            raise serializers.ValidationError({'email': 'Email does not match.'})

        if otp != user.otp:
            raise serializers.ValidationError({'otp': 'Invalid OTP.'})

        # Check OTP expiry
        if user.otp_created_at:
            elapsed = (timezone.now() - user.otp_created_at).total_seconds()
            if elapsed > OTP_EXPIRY_MINUTES * 60:
                raise serializers.ValidationError({'otp': 'OTP has expired. Please request a new one.'})

        user.password = make_password(validated_data.get('password'))
        user.otp = None
        user.otp_created_at = None
        user.save()
        return user