from django.shortcuts import render
from rest_framework import viewsets
from . import models,serializers
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class CourseViewSet(viewsets.ModelViewSet):
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer
    
    
class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = models.Enrollment.objects.all()
    serializer_class = serializers.EnrollmentSerializer
    permission_classes = [IsAuthenticated] 
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return models.Enrollment.objects.none()
        if user.role == 'student':
            return self.queryset.filter(student=user)
        elif user.role == 'instructor':
            return self.queryset.filter(course__created_by=user)
        return self.queryset
    
class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = models.Assessment.objects.all()
    serializer_class = serializers.AssessmentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return self.queryset.filter(enrollment__student=user)
        elif user.role == 'instructor':
            return self.queryset.filter(course__created_by=user)
        return self.queryset

class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = models.Submission.objects.all()
    serializer_class = serializers.SubmissionSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return self.queryset.filter(student=user)
        elif user.role == 'instructor':
            return self.queryset.filter(assessment__course__created_by=user)
        return self.queryset