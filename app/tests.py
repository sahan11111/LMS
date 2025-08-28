from django.test import TestCase
from .models import Course, Enrollment, Assessment, Submission
# Create your tests here.
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient           
from rest_framework import status
from django.urls import reverse     
import json
from rest_framework.authtoken.models import Token
from core.models import User as CustomUser
from .serializers import CourseSerializer, EnrollmentSerializer
from . import models
from django.utils import timezone
from datetime import timedelta
