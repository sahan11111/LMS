from django.urls import path,include
from .import views
from rest_framework import routers
router=routers.DefaultRouter()
router.register('Course',views.CourseViewSet)
router.register('Enrollment',views.EnrollmentViewSet)
router.register('Assessment',views.AssessmentViewSet)
router.register('Submission',views.SubmissionViewSet)
router.register('Sponsor',views.SponsorViewSet)
router.register('Sponsorship',views.SponsorshipViewSet)
router.register('Notification',views.NotificationViewSet)
router.register('EmailLog',views.EmailLogViewSet)
router.register('Dashboard',views.DashboardViewSet,basename='dashboard')
router.register('Quiz',views.QuizViewSet,basename='quiz')
urlpatterns = [
    path('', include(router.urls)),
    path("QuizSubmissions/", views.StudentSubmissionView.as_view(), name="student-submissions"),
    path("QuizSubmissions/<int:pk>/", views.StudentSubmissionView.as_view(), name="student-submission-detail"),
]