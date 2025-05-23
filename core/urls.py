from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet

router = DefaultRouter()
router.register('profiles', ProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
