from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .permissions import *
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        user = self.request.user
        
        # Admin has full access 
        if user.is_authenticated and user.groups.filter(name="Admin").exists():
            permission_classes = [IsAdmin]
            
        # Instructor can create/update/delete own courses 
        elif user.is_authenticated and user.groups.filter(name="Instructor").exists():
            permission_classes = [IsInstructorOrReadOnly]
            
        # Students & Sponsors can read-only 
        else:
            permission_classes = [ReadOnly]
            '''# Unauthenticated users = Read-only
            # permission_classes = [IsAuthenticatedOrReadOnly]'''
        return [p() for p in permission_classes]

    def get_queryset(self):
        user = self.request.user
        
        # Swagger fake view or unauthenticated users see no enrollments to avoid errors and protect data
        if getattr(self, 'swagger_fake_view', False):
            return Course.objects.none()
        
         # Admin sees all
        if user.is_authenticated and user.groups.filter(name="Admin").exists(): 
            return Course.objects.all()
         # Instructor sees own courses only
         
        elif user.is_authenticated and user.groups.filter(name="Instructor").exists(): 
            return Course.objects.filter(created_by=user)
        
        # Students & Sponsors see all (read-only)
        else:  
            return Course.objects.all()


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    def get_permissions(self):
        user = self.request.user
        #  If user is not authenticated, allow only authenticated permission (can be changed to AllowAny)
        if not user.is_authenticated:
            return [IsAuthenticated()]  

        # Check if user is Admin, grant full admin permissions
        if user.groups.filter(name="Admin").exists():
            return [IsAdmin()]

        # If user is Instructor, allow instructor-specific permissions (CRUD on own courses)
        elif user.groups.filter(name="Instructor").exists():
            return [IsInstructor()]

        # If user is Student, allow student-specific permissions
        elif user.role == 'student':
            return [IsStudent()]

        # If user is Sponsor, allow sponsor-specific permissions
        elif user.role == 'sponsor':
            return [IsSponsor()]

        # Default fallback permission
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        
        # Swagger fake view or unauthenticated users see no enrollments to avoid errors and protect data
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Enrollment.objects.none()

        # Admin can see all enrollments
        if user.groups.filter(name="Admin").exists():
            return self.queryset.all()

        # Instructor sees enrollments related to their courses only
        if user.groups.filter(name="Instructor").exists():
            return self.queryset.filter(course__created_by=user)

        #  Student sees only their own enrollments
        if user.role == 'student':
            return self.queryset.filter(student=user)

        #  Sponsor sees enrollments of students they sponsor (adjust 'sponsored_by' accordingly)
        if user.role == 'sponsor':
            return self.queryset.filter(student__sponsored_by=user)

        #  If none of above, return no enrollments
        return Enrollment.objects.none()


class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer

    def get_permissions(self):
        user = self.request.user
        #  If unauthenticated, default permission (can be adjusted)
        if not user.is_authenticated:
            return [IsAuthenticated()]

        # Admin has full access
        if user.groups.filter(name="Admin").exists():
            return [IsAdmin()]

        # Instructor can create/manage own assessments
        elif user.groups.filter(name="Instructor").exists():
            return [IsInstructorOrReadOnly()]

        # Student can view assessments for courses they are enrolled in
        elif user.role == 'student':
            return [IsStudent()]

        # Sponsor permission (usually no direct access to assessments)
        elif user.role == 'sponsor':
            return [IsSponsor()]

        # Default fallback
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        # Swagger view or unauthenticated = no data
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Assessment.objects.none()

        # Admin sees all assessments
        if user.groups.filter(name="Admin").exists():
            return self.queryset.all()

        # Instructor sees assessments only for their courses
        if user.groups.filter(name="Instructor").exists():
            return self.queryset.filter(course__created_by=user)

        #  Student sees assessments only in their enrolled courses
        if user.role == 'student':
            enrolled_courses = Enrollment.objects.filter(student=user).values_list('course', flat=True)
            return self.queryset.filter(course__in=enrolled_courses)

        #  Sponsors don’t see assessments by default
        if user.role == 'sponsor':
            return Assessment.objects.none()

        #  Default no data
        return Assessment.objects.none()


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    def get_permissions(self):
        user = self.request.user
        #  Default permission for unauthenticated users
        if not user.is_authenticated:
            return [IsAuthenticated()]

        # Admin full access
        if user.groups.filter(name="Admin").exists():
            return [IsAdmin()]

        # Instructor can manage submissions for own courses
        elif user.groups.filter(name="Instructor").exists():
            return [IsInstructorOrReadOnly()]

        # Student can view and submit their own submissions
        elif user.role == 'student':
            return [IsStudent()]

        # Sponsor permissions (usually no direct access)
        elif user.role == 'sponsor':
            return [IsSponsor()]

        # Default fallback permission
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        # No data for swagger or unauthenticated
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Submission.objects.none()

        # Admin sees all submissions
        if user.groups.filter(name="Admin").exists():
            return self.queryset.all()

        # Instructor sees submissions for assessments in their courses
        if user.groups.filter(name="Instructor").exists():
            return self.queryset.filter(assessment__course__created_by=user)

        #  Student sees only their submissions
        if user.role == 'student':
            return self.queryset.filter(student=user)

        #  Sponsors don’t see submissions
        if user.role == 'sponsor':
            return Submission.objects.none()

        #  Default no data
        return Submission.objects.none()
    
    
class SponsorViewSet(viewsets.ModelViewSet):
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer

    def get_permissions(self):
        user = self.request.user
        # Default permission for unauthenticated users
        if not user.is_authenticated:
            return [IsAuthenticated()]

        # Admin full access
        if user.groups.filter(name="Admin").exists():
            return [IsAdmin()]

        # Sponsors can manage their own sponsorships
        elif user.role == 'sponsor':
            return [IsSponsor()]

        # Instructors and Students typically don’t manage sponsorships
        elif user.groups.filter(name="Instructor").exists() or user.role == 'student':
            return [IsAuthenticatedOrReadOnly()]

        # Default fallback permission
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        # No data for swagger or unauthenticated
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Sponsor.objects.none()

        # Admin sees all sponsorships
        if user.groups.filter(name="Admin").exists():
            return self.queryset.all()

        # Sponsors see only their own sponsorships
        if user.role == 'sponsor':
            return self.queryset.filter(sponsor=user)

        # Instructors and Students typically don’t see sponsorships
        if user.groups.filter(name="Instructor").exists() or user.role == 'student':
            return Sponsor.objects.none()

        # Default no data
        return Sponsor.objects.none()
    
class SponsorshipViewSet(viewsets.ModelViewSet):
    queryset = Sponsorship.objects.all()
    serializer_class = SponsorshipSerializer

    def get_permissions(self):
        user = self.request.user
        # Default permission for unauthenticated users
        if not user.is_authenticated:
            return [IsAuthenticated()]

        # Admin full access
        if user.groups.filter(name="Admin").exists():
            return [IsAdmin()]

        # Sponsors can manage sponsorships they created
        elif user.role == 'sponsor':
            return [IsSponsor()]

        # Instructors and Students typically don’t manage sponsorships
        elif user.groups.filter(name="Instructor").exists() or user.role == 'student':
            return [IsAuthenticatedOrReadOnly()]

        # Default fallback permission
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        # No data for swagger or unauthenticated
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Sponsorship.objects.none()

        # Admin sees all sponsorships
        if user.groups.filter(name="Admin").exists():
            return self.queryset.all()

        # Sponsors see only sponsorships they created
        if user.role == 'sponsor':
            return self.queryset.filter(sponsor=user)

        # Instructors and Students typically don’t see sponsorships
        if user.groups.filter(name="Instructor").exists() or user.role == 'student':
            return Sponsorship.objects.none()

        # Default no data
        return Sponsorship.objects.none()
    
class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        data = {}

        if user.groups.filter(name="Admin").exists():
            data['total_users'] = User.objects.count()
            data['total_courses'] = Course.objects.count()
            data['total_enrollments'] = Enrollment.objects.count()
            data['total_assessments'] = Assessment.objects.count()
            data['total_submissions'] = Submission.objects.count()
            data['total_sponsors'] = Sponsor.objects.count()
            data['total_sponsorships'] = Sponsorship.objects.count()

        elif user.groups.filter(name="Instructor").exists():
            data['my_courses'] = Course.objects.filter(created_by=user).count()
            data['my_enrollments'] = Enrollment.objects.filter(course__created_by=user).count()
            data['my_assessments'] = Assessment.objects.filter(course__created_by=user).count()
            data['my_submissions'] = Submission.objects.filter(assessment__course__created_by=user).count()

        elif user.role == 'student':
            data['my_enrollments'] = Enrollment.objects.filter(student=user).count()
            data['my_courses'] = Course.objects.filter(enrollment__student=user).distinct().count()
            data['my_assessments'] = Assessment.objects.filter(course__enrollment__student=user).distinct().count()
            data['my_submissions'] = Submission.objects.filter(student=user).count()

        elif user.role == 'sponsor':
            sponsored_students = User.objects.filter(sponsorship__sponsor__user=user).distinct()
            data['sponsored_students'] = sponsored_students.count()
            data['sponsorships'] = Sponsorship.objects.filter(sponsor__user=user).count()

        return Response(data)
    


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # No data for swagger or unauthenticated
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Notification.objects.none()

        # Admin sees all notifications
        if user.groups.filter(name="Admin").exists():
            return self.queryset.all()

        # Users see only their own notifications
        return self.queryset.filter(user=user)
    
class EmailLogViewSet(viewsets.ModelViewSet):
    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # No data for swagger or unauthenticated
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return EmailLog.objects.none()

        # Admin sees all email logs
        if user.groups.filter(name="Admin").exists():
            return self.queryset.all()

        # Users see only their own email logs
        return self.queryset.filter(user=user)
