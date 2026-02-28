from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('user', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
     path('create-superuser/', views.SuperUserCreateAPIView.as_view(), name='create-superuser'),
]