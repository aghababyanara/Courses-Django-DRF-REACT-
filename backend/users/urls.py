from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, PublicProfileViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', PublicProfileViewSet, basename='public-profile')

urlpatterns = [
    path('', include(router.urls)),
]
