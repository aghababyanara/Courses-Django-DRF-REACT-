from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.db.models.signals import post_delete
from django.dispatch import receiver
from autoslug import AutoSlugField
from users.models import User


class CourseCategory(models.Model):
  name = models.CharField(max_length=100, unique=True)
  description = models.TextField(blank=True)

  def __str__(self):
    return self.name


class Course(models.Model):
  DIFFICULTY_LEVELS = (
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
  )

  title = models.CharField(max_length=200)
  slug = AutoSlugField(
    populate_from='title',
    unique=True,
    always_update=False,
    sep='-',
    max_length=200
  )
  instructor = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='courses_taught',
    limit_choices_to={'role': User.Role.INSTRUCTOR}
  )
  students = models.ManyToManyField(
    User,
    related_name='courses_enrolled',
    blank=True,
    limit_choices_to={'role': User.Role.STUDENT}
  )
  category = models.ForeignKey(
    CourseCategory,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='courses'
  )
  short_description = models.CharField(max_length=300)
  full_description = models.TextField()
  difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
  price = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0.00,
    validators=[MinValueValidator(0),
                MaxValueValidator(1000000.00)]
  )
  duration_hours = models.PositiveIntegerField(default=0)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  is_published = models.BooleanField(
    default=False,
    verbose_name="Published",
    help_text="Check to publish course. Uncheck to save as draft."
  )
  thumbnail = models.ImageField(
    upload_to='course_thumbnails/',
    validators=[
      FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
    ],
    blank=True,
    null=True
  )
  average_rating = models.FloatField(
    default=0.0,
    validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
  )

  class Meta:
    ordering = ['-created_at']
    indexes = [
      models.Index(fields=['slug']),
      models.Index(fields=['difficulty']),
      models.Index(fields=['average_rating']),
      models.Index(fields=['category']),
    ]
    verbose_name = 'Course'
    verbose_name_plural = 'Courses'

  def __str__(self):
    return self.title

  def update_average_rating(self):
    reviews = self.reviews.all()
    if reviews.exists():
      self.average_rating = round(
        sum([r.rating for r in reviews]) / reviews.count(),
        1
      )
    else:
      self.average_rating = 0.0
    self.save()


class Lesson(models.Model):
  CONTENT_TYPES = (
    ('video', 'Video'),
    ('article', 'Article'),
    ('assignment', 'Assignment'),
  )

  course = models.ForeignKey(
    Course,
    on_delete=models.CASCADE,
    related_name='lessons'
  )
  title = models.CharField(max_length=200)
  order = models.PositiveIntegerField(
    validators=[MinValueValidator(1)]
  )
  content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
  content = models.TextField()
  duration_minutes = models.PositiveIntegerField(default=0)
  is_free = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['order']
    unique_together = ('course', 'order')
    verbose_name = 'Lesson'
    verbose_name_plural = 'Lessons'


  def __str__(self):
    return f"{self.course.title} - {self.order}. {self.title}"

class LessonResource(models.Model):
  lesson = models.ForeignKey(
    'Lesson',
    on_delete=models.CASCADE,
    related_name='resources'
  )
  file = models.FileField(
    upload_to='lesson_resources/',
    validators=[
      FileExtensionValidator(
        allowed_extensions=['pdf', 'zip', 'docx', 'pptx', 'txt']
      )
    ],
    help_text="Allowed formats: PDF, ZIP, DOCX, PPTX, TXT"
  )
  name = models.CharField(max_length=255)
  uploaded_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-uploaded_at']
    indexes = [
      models.Index(fields=['lesson']),
    ]

  def __str__(self):
    return self.name or self.file.name


class Enrollment(models.Model):
  student = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='enrollments'
  )
  course = models.ForeignKey(
    Course,
    on_delete=models.CASCADE,
    related_name='enrollments'
  )
  enrolled_at = models.DateTimeField(auto_now_add=True)
  completed_at = models.DateTimeField(null=True, blank=True)
  progress = models.DecimalField(
    max_digits=5,
    decimal_places=2,
    default=0.0,
    validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
  )

  class Meta:
    unique_together = ('student', 'course')
    indexes = [
      models.Index(fields=['enrolled_at']),
      models.Index(fields=['progress']),
    ]

  def __str__(self):
    return f"{self.student.username} enrolled in {self.course.title}"


class CourseReview(models.Model):
  student = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='reviews'
  )
  course = models.ForeignKey(
    Course,
    on_delete=models.CASCADE,
    related_name='reviews'
  )
  rating = models.PositiveIntegerField(
    validators=[MinValueValidator(1), MaxValueValidator(5)]
  )
  comment = models.TextField(blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = ('student', 'course')
    ordering = ['-created_at']

  def __str__(self):
    return f"Review by {self.student} for {self.course}"

  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    self.course.update_average_rating()

  def delete(self, *args, **kwargs):
    course = self.course
    super().delete(*args, **kwargs)
    course.update_average_rating()

