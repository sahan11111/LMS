from django.shortcuts import render
from rest_framework import viewsets
from . import models,serializers
# Create your views here.

class CourseViewSet(viewsets.ModelViewSet):
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer
    