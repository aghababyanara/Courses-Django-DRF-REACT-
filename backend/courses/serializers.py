from rest_framework import serializers
from .models import CourseCategory, Course, Lesson, LessonResource, Enrollment, CourseReview
from users.serializers import UserSerializer


class CourseCategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = CourseCategory
    fields = ['id', 'name', 'description']
    read_only_fields = ['id']


class LessonResourceSerializer(serializers.ModelSerializer):
  class Meta:
    model = LessonResource
    fields = ['id', 'name', 'file', 'uploaded_at']
    read_only_fields = ['id', 'uploaded_at']


class LessonSerializer(serializers.ModelSerializer):
  resources = LessonResourceSerializer(many=True, read_only=True)

  class Meta:
    model = Lesson
    fields = [
      'id', 'order', 'title', 'content_type',
      'content', 'duration_minutes', 'is_free',
      'created_at', 'resources'
    ]
    read_only_fields = ['id', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
  instructor = UserSerializer(read_only=True)
  category = CourseCategorySerializer(read_only=True)
  lessons = LessonSerializer(many=True, read_only=True)
  thumbnail_url = serializers.SerializerMethodField()
  enrollment_status = serializers.SerializerMethodField()

  class Meta:
    model = Course
    fields = [
      'id', 'title', 'slug', 'instructor', 'category',
      'short_description', 'full_description', 'difficulty',
      'price', 'duration_hours', 'thumbnail', 'thumbnail_url',
      'average_rating', 'is_published', 'created_at', 'lessons',
      'enrollment_status', 'students'
    ]
    read_only_fields = [
      'id', 'slug', 'average_rating', 'created_at',
      'instructor', 'enrollment_status'
    ]
    extra_kwargs = {
      'thumbnail': {'write_only': True},
      'students': {'read_only': True}
    }

  def get_thumbnail_url(self, obj):
    if obj.thumbnail:
      return obj.thumbnail.url
    return None

  def get_enrollment_status(self, obj):
    request = self.context.get('request')
    if request and request.user.is_authenticated:
      return obj.enrollments.filter(student=request.user).exists()
    return False


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
  class Meta:
    model = Course
    fields = [
      'title', 'category', 'short_description', 'full_description',
      'difficulty', 'price', 'duration_hours', 'thumbnail', 'is_published'
    ]


class EnrollmentSerializer(serializers.ModelSerializer):
  student = UserSerializer(read_only=True)
  course = serializers.PrimaryKeyRelatedField(read_only=True)

  class Meta:
    model = Enrollment
    fields = ['id', 'student', 'course', 'enrolled_at', 'progress', 'completed_at']
    read_only_fields = ['id', 'enrolled_at']


class EnrollmentCreateSerializer(serializers.ModelSerializer):
  class Meta:
    model = Enrollment
    fields = ['course']
    extra_kwargs = {'course': {'required': True}}

  def validate(self, data):
    user = self.context['request'].user
    if Enrollment.objects.filter(student=user, course=data['course']).exists():
      raise serializers.ValidationError("You are already enrolled in this course")
    return data


class CourseReviewSerializer(serializers.ModelSerializer):
  student = UserSerializer(read_only=True)

  class Meta:
    model = CourseReview
    fields = ['id', 'student', 'course', 'rating', 'comment', 'created_at', 'updated_at']
    read_only_fields = ['id', 'created_at', 'updated_at', 'student']
    extra_kwargs = {'course': {'required': True}}

  def validate_rating(self, value):
    if not (1 <= value <= 5):
      raise serializers.ValidationError("Rating must be between 1 and 5")
    return value

  def validate(self, data):
    user = self.context['request'].user
    course = data.get('course')
    if CourseReview.objects.filter(student=user, course=course).exists():
      raise serializers.ValidationError("You have already reviewed this course")
    return data


class CourseDetailSerializer(CourseSerializer):
  reviews = serializers.SerializerMethodField()

  class Meta(CourseSerializer.Meta):
    fields = CourseSerializer.Meta.fields + ['reviews']

  def get_reviews(self, obj):
    reviews = obj.reviews.all().order_by('-created_at')[:10]
    return CourseReviewSerializer(reviews, many=True).data