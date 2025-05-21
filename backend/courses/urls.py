# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseCategoryViewSet,
    CourseViewSet,
    LessonViewSet,
    LessonResourceViewSet,
    EnrollmentViewSet,
    CourseReviewViewSet
)

router = DefaultRouter()
router.register(r'course-categories', CourseCategoryViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'lesson-resources', LessonResourceViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'reviews', CourseReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]