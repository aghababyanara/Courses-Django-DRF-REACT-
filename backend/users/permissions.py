from rest_framework import permissions


class IsSelfOrAdmin(permissions.BasePermission):
  def has_object_permission(self, request, view, obj):
    return request.user.is_authenticated and (
        request.user.is_admin or obj == request.user
    )

class IsInstructor(permissions.BasePermission):
  def has_permission(self, request, view):
    return request.user.is_authenticated and request.user.is_instructor

  def has_object_permission(self, request, view, obj):
    return self.has_permission(request, view)


class IsAdminUser(permissions.BasePermission):
  def has_permission(self, request, view):
    return request.user.is_authenticated and request.user.is_admin
