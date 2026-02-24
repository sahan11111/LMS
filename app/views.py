from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from django.db import models as django_models

from .models import (
    Course, Enrollment, Assessment, Submission, Sponsor, Sponsorship,
    Notification, EmailLog, Quiz, StudentSubmission,
)
from .serializers import (
    CourseSerializer, EnrollmentSerializer, AssessmentSerializer,
    SubmissionSerializer, SponsorSerializer, SponsorshipSerializer,
    NotificationSerializer, EmailLogSerializer, QuizSerializer,
    StudentSubmissionSerializer,
)
from .permissions import (
    IsAdmin, IsInstructor, IsInstructorOrReadOnly, IsStudent, IsSponsor, ReadOnly,
)
from .pagination import LMSPageNumberPagination


# ─────────────── Helper ───────────────
def _user_has_role(user, role):
    """Check role via role field or group membership."""
    if not user or not user.is_authenticated:
        return False
    return user.role == role.lower() or user.groups.filter(name=role.capitalize()).exists()


# ─────────────── Course ───────────────
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('id')
    serializer_class = CourseSerializer
    pagination_class = LMSPageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def get_permissions(self):
        user = self.request.user
        if user.is_authenticated and _user_has_role(user, 'admin'):
            return [IsAdmin()]
        elif user.is_authenticated and _user_has_role(user, 'instructor'):
            return [IsInstructorOrReadOnly()]
        return [ReadOnly()]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False):
            return Course.objects.none()

        qs = Course.objects.all()
        if user.is_authenticated and _user_has_role(user, 'admin'):
            return qs.order_by('id')
        elif user.is_authenticated and _user_has_role(user, 'instructor'):
            return qs.filter(created_by=user).order_by('id')
        return qs.order_by('id')


# ─────────────── Enrollment ───────────────
class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all().order_by('id')
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LMSPageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['course__id']

    def get_permissions(self):
        user = self.request.user
        if _user_has_role(user, 'admin'):
            return [IsAdmin()]
        elif _user_has_role(user, 'instructor'):
            return [IsInstructor()]
        elif _user_has_role(user, 'student'):
            return [IsStudent()]
        elif _user_has_role(user, 'sponsor'):
            return [IsSponsor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Enrollment.objects.none()

        qs = Enrollment.objects.all()
        if _user_has_role(user, 'admin'):
            return qs.order_by('id')
        if _user_has_role(user, 'instructor'):
            return qs.filter(course__created_by=user).order_by('id')
        if _user_has_role(user, 'student'):
            return qs.filter(student=user).order_by('id')
        if _user_has_role(user, 'sponsor'):
            return qs.filter(student__sponsorships__sponsor__user=user).distinct().order_by('id')
        return qs.none()

    def perform_create(self, serializer):
        user = self.request.user
        if _user_has_role(user, 'student'):
            serializer.save(student=user)
        else:
            raise PermissionDenied('Only students can enroll in courses.')


# ─────────────── Assessment ───────────────
class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        user = self.request.user
        if not user.is_authenticated:
            return [IsAuthenticated()]
        if _user_has_role(user, 'admin'):
            return [IsAdmin()]
        elif _user_has_role(user, 'instructor'):
            return [IsInstructor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Assessment.objects.none()

        if _user_has_role(user, 'admin'):
            return self.queryset.all()
        if _user_has_role(user, 'instructor'):
            return self.queryset.filter(course__created_by=user)
        if _user_has_role(user, 'student'):
            enrolled_courses = Enrollment.objects.filter(student=user).values_list('course', flat=True)
            return self.queryset.filter(course__in=enrolled_courses)
        return Assessment.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not (_user_has_role(user, 'admin') or _user_has_role(user, 'instructor')):
            raise PermissionDenied('Only Admins or Instructors can create assessments.')
        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        if serializer.instance.module and 'module' in serializer.validated_data:
            raise PermissionDenied('Cannot change the module once Assessment is created.')
        course = serializer.validated_data.get('course')
        if course and _user_has_role(user, 'instructor') and course.created_by != user:
            raise PermissionDenied('You can only assign assessments to your own courses.')
        serializer.save()


# ─────────────── Submission ───────────────
class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return [IsAuthenticated()]
        if _user_has_role(user, 'admin'):
            return [IsAdmin()]
        elif _user_has_role(user, 'instructor'):
            return [IsInstructor()]
        elif _user_has_role(user, 'student'):
            return [IsStudent()]
        elif _user_has_role(user, 'sponsor'):
            return [IsSponsor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Submission.objects.none()

        if _user_has_role(user, 'admin'):
            return Submission.objects.all()
        if _user_has_role(user, 'instructor'):
            return Submission.objects.filter(assessment__course__created_by=user)
        if _user_has_role(user, 'student'):
            return Submission.objects.filter(student=user)
        return Submission.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not _user_has_role(user, 'student'):
            raise PermissionDenied('Only students can submit assessments.')

        assessment = serializer.validated_data.get('assessment')
        if not Enrollment.objects.filter(student=user, course=assessment.course).exists():
            raise PermissionDenied('You must be enrolled in the course to submit.')

        serializer.save(student=user)

    @action(detail=True, methods=['patch'], url_path='grade')
    def grade_submission(self, request, pk=None):
        submission = self.get_object()
        user = request.user

        if not _user_has_role(user, 'instructor'):
            return Response(
                {'error': 'Permission denied: Only instructors can grade submissions.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if submission.assessment.course.created_by_id != user.id:
            return Response(
                {'error': 'Permission denied: You can only grade submissions for your own courses.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        score = request.data.get('score')
        if score is None:
            return Response({'error': 'Score is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            score = float(score)
        except (ValueError, TypeError):
            return Response({'error': 'Score must be a number.'}, status=status.HTTP_400_BAD_REQUEST)

        if score < 0 or score > submission.assessment.max_score:
            return Response(
                {'error': f'Score must be between 0 and {submission.assessment.max_score}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        submission.score = score
        submission.save()
        return Response(
            {'message': 'Submission graded successfully', 'score': submission.score},
            status=status.HTTP_200_OK,
        )


# ─────────────── Sponsor ───────────────
class SponsorViewSet(viewsets.ModelViewSet):
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return [IsAuthenticated()]
        if _user_has_role(user, 'admin'):
            return [IsAdmin()]
        elif _user_has_role(user, 'sponsor'):
            return [IsSponsor()]
        elif _user_has_role(user, 'instructor'):
            return [IsInstructorOrReadOnly()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Sponsor.objects.none()

        if _user_has_role(user, 'admin'):
            return Sponsor.objects.all()
        if _user_has_role(user, 'sponsor'):
            return Sponsor.objects.filter(user=user)
        return Sponsor.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if _user_has_role(user, 'sponsor'):
            serializer.save(user=user)
        else:
            raise PermissionDenied('Only sponsors can create sponsor profiles.')


# ─────────────── Sponsorship ───────────────
class SponsorshipViewSet(viewsets.ModelViewSet):
    queryset = Sponsorship.objects.all()
    serializer_class = SponsorshipSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        user = self.request.user
        if _user_has_role(user, 'admin'):
            return [IsAdmin()]
        elif _user_has_role(user, 'sponsor'):
            return [IsSponsor()]
        elif _user_has_role(user, 'instructor') or _user_has_role(user, 'student'):
            return [IsAuthenticatedOrReadOnly()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Sponsorship.objects.none()

        if _user_has_role(user, 'admin'):
            return Sponsorship.objects.all()
        if _user_has_role(user, 'sponsor'):
            return (
                Sponsorship.objects.filter(sponsor__user=user) |
                Sponsorship.objects.filter(status='pending')
            ).distinct()
        if _user_has_role(user, 'student'):
            return Sponsorship.objects.filter(student=user)
        return Sponsorship.objects.none()

    def perform_create(self, serializer):
        serializer.save()


# ─────────────── Dashboard ───────────────
class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        data = {}

        if _user_has_role(user, 'admin'):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            data['total_users'] = User.objects.count()
            data['total_courses'] = Course.objects.count()
            data['total_enrollments'] = Enrollment.objects.count()
            data['total_assessments'] = Assessment.objects.count()
            data['total_submissions'] = Submission.objects.count()
            data['total_sponsors'] = Sponsor.objects.count()
            data['total_sponsorships'] = Sponsorship.objects.count()
            data['total_notifications'] = Notification.objects.count()
            data['total_email_logs'] = EmailLog.objects.count()
            data['total_quizzes'] = Quiz.objects.count()

        elif _user_has_role(user, 'instructor'):
            data['my_courses'] = Course.objects.filter(created_by=user).count()
            data['my_enrollments'] = Enrollment.objects.filter(course__created_by=user).count()
            data['my_assessments'] = Assessment.objects.filter(course__created_by=user).count()
            data['my_submissions'] = Submission.objects.filter(assessment__course__created_by=user).count()
            data['my_quizzes'] = Quiz.objects.filter(course__created_by=user).count()

        elif _user_has_role(user, 'student'):
            data['my_enrollments'] = Enrollment.objects.filter(student=user).count()
            data['my_courses'] = Course.objects.filter(enrollments__student=user).distinct().count()
            data['my_assessments'] = Assessment.objects.filter(course__enrollments__student=user).distinct().count()
            data['my_submissions'] = Submission.objects.filter(student=user).count()
            data['my_notifications'] = Notification.objects.filter(user=user).count()
            data['my_quizzes'] = Quiz.objects.filter(course__enrollments__student=user).distinct().count()
            data['my_passed_quizzes'] = Quiz.objects.filter(
                submissions__student=user, submissions__passed=True
            ).distinct().count()
            data['my_pending_sponsorships'] = Sponsorship.objects.filter(student=user, status='pending').count()
            data['my_approved_sponsorships'] = Sponsorship.objects.filter(student=user, status='approved').count()
            data['my_rejected_sponsorships'] = Sponsorship.objects.filter(student=user, status='rejected').count()
            data['my_sponsors'] = Sponsor.objects.filter(sponsorships__student=user).distinct().count()

        elif _user_has_role(user, 'sponsor'):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            sponsored_students = User.objects.filter(sponsorships__sponsor__user=user).distinct()
            data['sponsored_students'] = sponsored_students.count()
            data['sponsorships'] = Sponsorship.objects.filter(sponsor__user=user).count()
            data['approved_sponsorships'] = Sponsorship.objects.filter(sponsor__user=user, status='approved').count()
            data['pending_sponsorships'] = Sponsorship.objects.filter(sponsor__user=user, status='pending').count()
            data['rejected_sponsorships'] = Sponsorship.objects.filter(sponsor__user=user, status='rejected').count()
            data['total_funds_provided'] = (
                Sponsorship.objects.filter(sponsor__user=user, status='approved')
                .aggregate(total=django_models.Sum('amount'))['total'] or 0
            )
            data['sponsored_students_list'] = [
                {'id': s.id, 'username': s.username} for s in sponsored_students
            ]

        return Response(data)


# ─────────────── Notification ───────────────
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Notification.objects.none()

        if _user_has_role(user, 'admin'):
            return Notification.objects.all()
        if _user_has_role(user, 'instructor'):
            return Notification.objects.filter(
                user__enrollments__course__created_by=user
            ).distinct()
        if _user_has_role(user, 'student'):
            return Notification.objects.filter(user=user)
        if _user_has_role(user, 'sponsor'):
            return Notification.objects.filter(
                user__sponsorships__sponsor__user=user
            ).distinct()
        return Notification.objects.none()

    def perform_create(self, serializer):
        if not _user_has_role(self.request.user, 'admin'):
            raise PermissionDenied('Only Admins can create notifications.')
        serializer.save()


# ─────────────── Email Log ───────────────
class EmailLogViewSet(viewsets.ModelViewSet):
    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return EmailLog.objects.none()

        if _user_has_role(user, 'admin'):
            return EmailLog.objects.all()
        return EmailLog.objects.filter(user=user)


# ─────────────── Quiz ───────────────
class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all().order_by('id')
    serializer_class = QuizSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def get_permissions(self):
        user = self.request.user
        if _user_has_role(user, 'admin'):
            return [IsAdmin()]
        elif _user_has_role(user, 'instructor'):
            return [IsInstructor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Quiz.objects.none()

        if _user_has_role(user, 'admin'):
            return self.queryset.all()
        elif _user_has_role(user, 'instructor'):
            return self.queryset.filter(course__created_by=user)
        elif _user_has_role(user, 'student'):
            enrolled_courses = Enrollment.objects.filter(student=user).values_list('course', flat=True)
            return self.queryset.filter(course__in=enrolled_courses)
        return Quiz.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        course = serializer.validated_data.get('course')

        if _user_has_role(user, 'instructor'):
            if course.created_by != user:
                raise PermissionDenied('Instructors can only create quizzes for their own courses.')
            serializer.save(created_by=user)
        elif _user_has_role(user, 'admin'):
            serializer.save(created_by=user)
        else:
            raise PermissionDenied('Only Admins or Instructors can create quizzes.')


# ─────────────── Student Quiz Submission ───────────────
class StudentSubmissionView(ListCreateAPIView, RetrieveAPIView):
    """
    Student can POST a quiz submission, GET all their submissions,
    or GET a single submission by ID.
    """
    serializer_class = StudentSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return StudentSubmission.objects.none()

        if _user_has_role(user, 'admin'):
            return StudentSubmission.objects.all()
        if _user_has_role(user, 'instructor'):
            return StudentSubmission.objects.filter(quiz__course__created_by=user)
        return StudentSubmission.objects.filter(student=user)