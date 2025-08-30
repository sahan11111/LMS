from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .permissions import *
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied

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
    permission_classes = [IsAuthenticated]  

    def get_permissions(self):
        user = self.request.user

        # Admin → full access to all enrollments
        if user.groups.filter(name="Admin").exists():
            return [IsAdmin()]

        # Instructor → manage enrollments for their own courses
        elif user.groups.filter(name="Instructor").exists():
            return [IsInstructor()]
        
        # Student → view and create their own enrollments
        elif user.groups.filter(name="Student").exists():
            return [IsStudent()]
        
        # Sponsor → view enrollments of their sponsored students
        elif user.groups.filter(name="Sponsor").exists():
            return [IsSponsor()]

        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        # Swagger view / unauthenticated → no data
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Enrollment.objects.none()

        # Admin → all enrollments
        if user.groups.filter(name="Admin").exists():
            return Enrollment.objects.all()

        # Instructor → enrollments only for their own courses
        if user.groups.filter(name="Instructor").exists():
            return Enrollment.objects.filter(course__created_by=user)

        # Student → only their own enrollments
        if user.groups.filter(name="Student").exists():
            return Enrollment.objects.filter(student=user)

        # Sponsor → enrollments of students they sponsor
        if user.groups.filter(name="Sponsor").exists():
            return Enrollment.objects.filter(student__sponsorship__sponsor__user=user).distinct()

        return Enrollment.objects.none()

    def perform_create(self, serializer):
        """Auto-assign student when creating an enrollment."""
        user = self.request.user

        # Only students can enroll
        if user.groups.filter(name="Student").exists():
            serializer.save(student=user)
        else:
            raise PermissionDenied("Only students can enroll in courses.")


class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated | ReadOnly]  # default

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
            return [IsInstructor()]

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
        if user.groups.filter(name="Student").exists():
            enrolled_courses = Enrollment.objects.filter(student=user).values_list('course', flat=True)
            return self.queryset.filter(course__in=enrolled_courses)
        #  Sponsors don’t see assessments by default
        if user.groups.filter(name="Sponsor").exists():
            return Assessment.objects.none()

        #  Default no data
        return Assessment.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.groups.filter(name="Admin").exists():
            serializer.save()
        elif user.groups.filter(name="Instructor").exists():
            course = serializer.validated_data.get("course")
            if course.created_by != user:
                raise PermissionDenied("You can only add assessments to your own courses.")
            serializer.save()
        else:
            raise PermissionDenied("Only Admins or Instructors can create assessments.")
class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]  # default

    def get_permissions(self):
        user = self.request.user

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

            # Swagger view / unauthenticated → no data
            if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
                return Submission.objects.none()

            # Admin → all submissions
            if user.groups.filter(name="Admin").exists():
                return Submission.objects.all()

            # Instructor → submissions only for assessments in their courses
            if user.groups.filter(name="Instructor").exists():
                return Submission.objects.filter(assessment__course__created_by=user)

            # Student → only their own submissions
            if user.groups.filter(name="Student").exists():
                return Submission.objects.filter(student=user)

            # Sponsor → no submissions
            if user.groups.filter(name="Sponsor").exists():
                return Submission.objects.none()

            return Submission.objects.none()

    def perform_create(self, serializer):
        """Auto-assign student when creating a submission."""
        user = self.request.user

        if not user.groups.filter(name="Student").exists():
            raise PermissionDenied("Only students can submit assessments.")

        assessment = serializer.validated_data.get("assessment")

        # Validate: student must be enrolled in this course
        is_enrolled = Enrollment.objects.filter(student=user, course=assessment.course).exists()
        if not is_enrolled:
            raise PermissionDenied("You must be enrolled in the course to submit.")

        serializer.save(student=user)
    
    
class SponsorViewSet(viewsets.ModelViewSet):
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer
    permission_classes = [IsAuthenticated]  # default
    
    def get_permissions(self):
        user = self.request.user

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

        # Swagger view / unauthenticated → no data
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Sponsorship.objects.none()

        # Admin → all sponsorships
        if user.groups.filter(name="Admin").exists():
            return Sponsorship.objects.all()

        # Sponsor → only their sponsorships
        if user.groups.filter(name="Sponsor").exists():
            return Sponsorship.objects.filter(sponsor=user)

        # Instructor/Student → no access
        return Sponsorship.objects.none()

    def perform_create(self, serializer):
        """Auto-assign sponsor when creating a sponsorship."""
        user = self.request.user

        if user.groups.filter(name="Sponsor").exists():
            serializer.save(sponsor=user)
        else:
            raise PermissionDenied("Only sponsors can create sponsorships.")
    
class SponsorshipViewSet(viewsets.ModelViewSet):
    queryset = Sponsorship.objects.all()
    serializer_class = SponsorshipSerializer
    permission_classes = [IsAuthenticated]  # default
    def get_permissions(self):
        user = self.request.user

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

        # Swagger view / unauthenticated → no data
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Sponsorship.objects.none()

        # Admin → all sponsorships
        if user.groups.filter(name="Admin").exists():
            return Sponsorship.objects.all()

        # Sponsor → only their sponsorships
        if user.groups.filter(name="Sponsor").exists():
            return Sponsorship.objects.filter(sponsor=user)

        # Instructor/Student → no access
        return Sponsorship.objects.none()

    def perform_create(self, serializer):
        """Auto-assign sponsor when creating a sponsorship."""
        user = self.request.user

        if user.groups.filter(name="Sponsor").exists():
            serializer.save(sponsor=user)
        else:
            raise PermissionDenied("Only sponsors can create sponsorships.")
    
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

        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Notification.objects.none()

        # Admin → all notifications
        if user.groups.filter(name="Admin").exists():
            return Notification.objects.all()

        # Instructor → notifications related to their courses/students
        if user.groups.filter(name="Instructor").exists():
            return Notification.objects.filter(course__created_by=user)

        # Student → only their notifications
        if user.groups.filter(name="Student").exists():
            return Notification.objects.filter(recipient=user)

        # Sponsor → notifications for their sponsored students
        if user.groups.filter(name="Sponsor").exists():
            return Notification.objects.filter(student__sponsorship__sponsor=user)

        return Notification.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.groups.filter(name="Admin").exists():
            serializer.save()
        else:
            raise PermissionDenied("Only Admins can create notifications.")
    
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
