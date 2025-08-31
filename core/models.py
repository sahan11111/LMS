from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager

# Create your models here.

#User model with role field
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
        ('sponsor', 'Sponsor'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    email=models.EmailField(unique=True)
    otp = models.CharField(max_length=255, null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS=[]
    
    objects=UserManager()