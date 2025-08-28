from django.urls import path,include
from .import views
from rest_framework import routers
router=routers.DefaultRouter()
router.register('Course',views.CourseViewSet)
router.register('Enrollment',views.EnrollmentViewSet)
router.register('Assessment',views.AssessmentViewSet)
router.register('Submission',views.SubmissionViewSet)
urlpatterns = [
    path('', include(router.urls)),
]