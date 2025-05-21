from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()

class IsInstructor(permissions.BasePermission):
    message = 'Only instructors can perform this action.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.INSTRUCTOR

class IsCourseOwner(permissions.BasePermission):
    message = 'You must be the owner of the course.'

    def has_object_permission(self, request, view, obj):
        return obj.instructor == request.user

class IsLessonCourseOwner(permissions.BasePermission):
    message = 'You must be the instructor of the course to modify this lesson.'

    def has_object_permission(self, request, view, obj):
        return obj.course.instructor == request.user

class IsLessonResourceCourseOwner(permissions.BasePermission):
    message = 'You must be the instructor of the course to modify this resource.'

    def has_object_permission(self, request, view, obj):
        return obj.lesson.course.instructor == request.user