# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import (
  CourseCategory,
  Course,
  Lesson,
  LessonResource,
  Enrollment,
  CourseReview
)
from .serializers import (
  CourseCategorySerializer,
  CourseSerializer,
  CourseCreateUpdateSerializer,
  CourseDetailSerializer,
  LessonSerializer,
  LessonResourceSerializer,
  EnrollmentSerializer,
  EnrollmentCreateSerializer,
  CourseReviewSerializer
)
from .permissions import (
  IsInstructor,
  IsCourseOwner,
  IsLessonCourseOwner,
  IsLessonResourceCourseOwner
)
from users.models import User


class CourseCategoryViewSet(viewsets.ModelViewSet):
  queryset = CourseCategory.objects.all()
  serializer_class = CourseCategorySerializer

  def get_permissions(self):
    if self.action in ['list', 'retrieve']:
      return [AllowAny()]
    return [IsAdminUser()]


class CourseViewSet(viewsets.ModelViewSet):
  queryset = Course.objects.all()

  def get_serializer_class(self):
    if self.action == 'retrieve':
      return CourseDetailSerializer
    elif self.action in ['create', 'update', 'partial_update']:
      return CourseCreateUpdateSerializer
    return CourseSerializer

  def get_permissions(self):
    if self.action == 'create':
      return [IsAuthenticated(), IsInstructor()]
    elif self.action in ['update', 'partial_update', 'destroy']:
      return [IsAuthenticated(), IsCourseOwner()]
    return [AllowAny()]

  def perform_create(self, serializer):
    serializer.save(instructor=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
  queryset = Lesson.objects.all()
  serializer_class = LessonSerializer
  permission_classes = [IsAuthenticated, IsLessonCourseOwner]

  def perform_create(self, serializer):
    course = serializer.validated_data['course']
    if course.instructor != self.request.user:
      raise PermissionDenied("You are not the instructor of this course.")
    serializer.save()


class LessonResourceViewSet(viewsets.ModelViewSet):
  queryset = LessonResource.objects.all()
  serializer_class = LessonResourceSerializer
  permission_classes = [IsAuthenticated, IsLessonResourceCourseOwner]

  def perform_create(self, serializer):
    lesson = serializer.validated_data['lesson']
    if lesson.course.instructor != self.request.user:
      raise PermissionDenied("You are not the instructor of this course.")
    serializer.save()


class EnrollmentViewSet(viewsets.ModelViewSet):
  queryset = Enrollment.objects.none()
  serializer_class = EnrollmentSerializer
  permission_classes = [IsAuthenticated]

  def get_queryset(self):
    return self.request.user.enrollments.all()

  def get_serializer_class(self):
    if self.action == 'create':
      return EnrollmentCreateSerializer
    return EnrollmentSerializer

  def perform_create(self, serializer):
    serializer.save(student=self.request.user)


class CourseReviewViewSet(viewsets.ModelViewSet):
  queryset = CourseReview.objects.none()
  serializer_class = CourseReviewSerializer
  permission_classes = [IsAuthenticated]

  def get_queryset(self):
    return self.request.user.reviews.all()

  def create(self, request, *args, **kwargs):
    course_id = request.data.get('course')
    if not course_id:
      return Response({'course': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if not Enrollment.objects.filter(student=request.user, course_id=course_id).exists():
      return Response({'detail': 'You must be enrolled to review this course.'}, status=status.HTTP_403_FORBIDDEN)
    return super().create(request, *args, **kwargs)

  def perform_create(self, serializer):
    serializer.save(student=self.request.user)