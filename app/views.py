from django.shortcuts import render
from rest_framework import viewsets,status,filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .permissions import *
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from .pagination import ProductPageNumberPagination
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by("id")
    serializer_class = CourseSerializer
    pagination_class=ProductPageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields =['title']
    

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
        qs=Course.objects.all()
        
        # Swagger fake view or unauthenticated users see no enrollments to avoid errors and protect data
        if getattr(self, 'swagger_fake_view', False):
            return Course.objects.none()
        
         # Admin sees all
        if user.is_authenticated and user.groups.filter(name="Admin").exists(): 
            return qs.order_by('id')
         # Instructor sees own courses only
         
        elif user.is_authenticated and user.groups.filter(name="Instructor").exists(): 
            return qs.filter(created_by=user).order_by('id')
        
        # Students & Sponsors see all (read-only)
        else:  
            return qs.order_by('id')


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all().order_by("id")
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]  
    pagination_class=ProductPageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields =['course__id']

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
        qs=Enrollment.objects.all()

        # Swagger view / unauthenticated → no data
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return qs.none()

        # Admin → all enrollments
        if user.groups.filter(name="Admin").exists():
            return qs.all().order_by('id')

        # Instructor → enrollments only for their own courses
        if user.groups.filter(name="Instructor").exists():
            return qs.filter(course__created_by=user).order_by('id')

        # Student → only their own enrollments
        if user.groups.filter(name="Student").exists():
            return qs.filter(student=user).order_by('id')

        # Sponsor → enrollments of students they sponsor
        if user.groups.filter(name="Sponsor").exists():
            return qs.filter(student__sponsorship__sponsor__user=user).distinct()

        return qs.none()

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
    permission_classes = [IsAuthenticated]  # default fallback

    def get_permissions(self):
        """
        Return appropriate permissions based on user group.
        """
        user = self.request.user

        # If unauthenticated, default permission
        if not user.is_authenticated:
            return [IsAuthenticated()]

        # Admin has full access
        if user.groups.filter(name="Admin").exists():
            return [IsAdmin()]

        # Instructor can manage own assessments
        elif user.groups.filter(name="Instructor").exists():
            return [IsInstructor()]

        # Default fallback for authenticated users
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Return queryset based on user role.
        """
        user = self.request.user

        # Swagger or unauthenticated: return empty queryset
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Assessment.objects.none()

        # Admin sees all assessments
        if user.groups.filter(name="Admin").exists():
            return self.queryset.all()

        # Instructor sees assessments only for their courses
        if user.groups.filter(name="Instructor").exists():
            return self.queryset.filter(course__created_by=user)

        # Student sees assessments only in enrolled courses
        if user.groups.filter(name="Student").exists():
            enrolled_courses = Enrollment.objects.filter(student=user).values_list('course', flat=True)
            return self.queryset.filter(course__in=enrolled_courses)

        # Sponsor sees no assessments by default
        if user.groups.filter(name="Sponsor").exists():
            return Assessment.objects.none()

        # Default fallback: empty queryset
        return Assessment.objects.none()

    def perform_create(self, serializer):
        """
        Control creation based on user role.
        Admins can create any assessment.
        Instructors can create only for their own courses.
        Others are forbidden.
        """
        user = self.request.user

        if not (user.groups.filter(name="Admin").exists() or user.groups.filter(name="Instructor").exists()):
            raise PermissionDenied("Only Admins or Instructors can create assessments.")

        # # Validate module (if provided) belongs to instructor's course
        # module_data = serializer.validated_data.get('module')
        # if module_data:
        #     if user.groups.filter(name="Instructor").exists() and module_data.get('course', None):
        #         # If module_data has a course field, ensure it matches assessment course
        #         if module_data['course'] != serializer.validated_data['course']:
        #             raise PermissionDenied("Module course must match the assessment course.")

        serializer.save()
        
    def perform_update(self, serializer):
        user = self.request.user
        if serializer.instance.module and 'module' in serializer.validated_data:
            raise PermissionDenied("Cannot change the module once Assessment is created.")
        # Check instructor cannot assign course to another instructor's course
        course = serializer.validated_data.get('course')
        if course and user.groups.filter(name="Instructor").exists() and course.created_by != user:
            raise PermissionDenied("You can only assign assessments to your own courses.")
        serializer.save()
        
    # def perform_update(self, serializer):
    #     """
    #     Prevent changing module after creation.
    #     Validate course updates for Instructors.
    #     """
    #     user = self.request.user

    #     if 'module' in serializer.validated_data:
    #         raise PermissionDenied("Module cannot be changed once the assessment is created.")

    #     course = serializer.validated_data.get('course')
    #     if course and user.groups.filter(name="Instructor").exists() and course.created_by != user:
    #         raise PermissionDenied("You can only assign assessments to your own courses.")

    #     serializer.save()
        
class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]  # default

    def get_permissions(self):
        user = self.request.user

        # If not logged in → deny
        if not user or not user.is_authenticated:
            return [IsAuthenticated()]  # Returns 401 instead of crashing

        # Admin full access
        if user.groups.filter(name="Admin").exists():
            return [IsAdmin()]

        # Instructor permissions
        elif user.groups.filter(name="Instructor").exists():
            return [IsInstructor()]

        # Student permissions
        elif getattr(user, "role", None) == "student" or user.groups.filter(name="Student").exists():
            return [IsStudent()]

        # Sponsor permissions
        elif getattr(user, "role", None) == "sponsor" or user.groups.filter(name="Sponsor").exists():
            return [IsSponsor()]

        # Fallback
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        # Swagger view / unauthenticated → no data
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return Submission.objects.none()

        # Admin → all submissions
        if user.groups.filter(name="Admin").exists():
            return Submission.objects.all()

        # Instructor → submissions only for assessments in their courses
        if user.groups.filter(name="Instructor").exists():
            return Submission.objects.filter(assessment__course__created_by=user)

        # Student → only their own submissions
        if user.groups.filter(name="Student").exists() or getattr(user, "role", None) == "student":
            return Submission.objects.filter(student=user)

        # Sponsor → no submissions
        if user.groups.filter(name="Sponsor").exists() or getattr(user, "role", None) == "sponsor":
            return Submission.objects.none()

        return Submission.objects.none()

    def perform_create(self, serializer):
        """Auto-assign student when creating a submission."""
        user = self.request.user

        if not user.groups.filter(name="Student").exists() and getattr(user, "role", None) != "student":
            raise PermissionDenied("Only students can submit assessments.")

        assessment = serializer.validated_data.get("assessment")

        # Validate: student must be enrolled in this course
        is_enrolled = Enrollment.objects.filter(student=user, course=assessment.course).exists()
        if not is_enrolled:
            raise PermissionDenied("You must be enrolled in the course to submit.")

        serializer.save(student=user)

    @action(detail=True, methods=["patch"], url_path="grade")
    def grade_submission(self, request, pk=None):
        submission = self.get_object()
        user = request.user

        # Step 1: Must be an instructor
        if not (user.groups.filter(name="Instructor").exists() or getattr(user, "role", "").lower() == "instructor"):
            return Response(
                {"error": "Permission denied: Only instructors can grade submissions."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Step 2: Check if instructor owns the course
        if submission.assessment.course.created_by_id != user.id:
            return Response(
                {"error": "Permission denied: You can only grade submissions for your own courses."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Step 3: Validate score input
        score = request.data.get("score")
        if score is None:
            return Response({"error": "Score is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            score = float(score)
        except ValueError:
            return Response({"error": "Score must be a number."}, status=status.HTTP_400_BAD_REQUEST)

        # Step 4: Save grade
        submission.score = score
        submission.save()

        return Response(
            {"message": "Submission graded successfully", "score": submission.score},
            status=status.HTTP_200_OK,
        )

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
        elif user.groups.filter(name="Instructor").exists() :
            return [IsInstructorOrReadOnly()]

        # Default fallback permission
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        # Swagger view / unauthenticated → no data
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Sponsor.objects.none()

        # Admin → all Sponsors
        if user.groups.filter(name="Admin").exists():
            return Sponsor.objects.all()

        # Sponsor → only their Sponsors
        if user.groups.filter(name="Sponsor").exists():
            return Sponsor.objects.filter(sponsor=user)

        # Instructor/Student → no access
        return Sponsor.objects.none()

    def perform_create(self, serializer):
        """Auto-assign sponsor when creating a Sponsor."""
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
        elif user.groups.filter(name="Instructor").exists() or user.groups.filter(name="Student").exists():
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
            # Sponsors see their sponsorships + pending requests
            return Sponsorship.objects.filter(sponsor__user=user) | Sponsorship.objects.filter(status="pending")

        # Student → only sponsorships for themselves
        if user.groups.filter(name="Student").exists():
            return Sponsorship.objects.filter(student=user)
        
        # Instructor/Student → no access
        return Sponsorship.objects.none()

    def perform_create(self, serializer):
        serializer.save()  
    
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
    queryset = models.Notification.objects.all()  # must define this
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Swagger or anonymous users → return empty queryset
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return models.Notification.objects.none()

        # Admin → all notifications
        if user.groups.filter(name="Admin").exists():
            return models.Notification.objects.all()

        # Instructor → notifications for students enrolled in their courses
        if user.groups.filter(name="Instructor").exists():
            return models.Notification.objects.filter(
                user__enrollment__course__created_by=user
            ).distinct()

        # Student → their own notifications
        if user.groups.filter(name="Student").exists():
            return models.Notification.objects.filter(user=user)

        # Sponsor → notifications for their sponsored students
        if user.groups.filter(name="Sponsor").exists():
            return models.Notification.objects.filter(
                user__sponsorship__sponsor=user
            ).distinct()

        return models.Notification.objects.none()

    def perform_create(self, serializer):
        if not self.request.user.groups.filter(name="Admin").exists():
            raise PermissionDenied("Only Admins can create notifications.")
        serializer.save()
    
class EmailLogViewSet(viewsets.ModelViewSet):
    queryset = models.EmailLog.objects.all()  #  must define this
    serializer_class = EmailLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Short-circuit for swagger or anonymous users
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return models.EmailLog.objects.none()  #  use model directly if queryset may be None

        # Admin sees all
        if user.groups.filter(name="Admin").exists():
            return models.EmailLog.objects.all()

        # Others see only their own email logs
        return models.EmailLog.objects.filter(user=user)



class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all().order_by("id")
    serializer_class = QuizSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def get_permissions(self):
        user = self.request.user
        if user.groups.filter(name="Admin").exists():
            return [IsAdmin()]
        elif user.groups.filter(name="Instructor").exists():
            return [IsInstructor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Quiz.objects.none()

        if user.groups.filter(name="Admin").exists():
            return self.queryset.all()
        elif user.groups.filter(name="Instructor").exists():
            return self.queryset.filter(course__created_by=user)
        elif user.groups.filter(name="Student").exists():
            enrolled_courses = models.Enrollment.objects.filter(student=user).values_list('course', flat=True)
            return self.queryset.filter(course__in=enrolled_courses)
        return Quiz.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        course = serializer.validated_data.get('course')

        if user.groups.filter(name="Instructor").exists():
            if course.created_by != user:
                raise serializers.ValidationError("Instructors can only create quizzes for their own courses.")
            serializer.save(created_by=user)
        else:
            serializer.save()


class StudentSubmissionView(ListCreateAPIView, RetrieveAPIView):
    """
    Student can create (POST) a submission, list all their submissions (GET),
    and retrieve a single submission by ID (GET /<id>/).
    """
    serializer_class = StudentSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Prevent errors when generating Swagger docs or if user is anonymous
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return models.StudentSubmission.objects.none()

        if user.groups.filter(name="Admin").exists():
            return models.StudentSubmission.objects.all()

        if user.groups.filter(name="Instructor").exists():
            # Instructors can see submissions for their own courses
            return models.StudentSubmission.objects.filter(quiz__course__created_by=user)

        # Students see only their own submissions
        return models.StudentSubmission.objects.filter(student=user)

