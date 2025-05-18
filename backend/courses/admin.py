from django.contrib import admin
from django.utils.html import format_html
from .models import *


class CourseCategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'course_count')
  search_fields = ('name',)

  def course_count(self, obj):
    return obj.courses.count()

  course_count.short_description = 'Courses Count'


admin.site.register(CourseCategory, CourseCategoryAdmin)


class LessonResourceInline(admin.TabularInline):
  model = LessonResource
  extra = 1
  fields = ('name', 'file', 'uploaded_at')
  readonly_fields = ('uploaded_at',)


class LessonInline(admin.StackedInline):
  model = Lesson
  extra = 0
  fields = ('order', 'title', 'content_type', 'duration_minutes', 'is_free')
  readonly_fields = ('created_at',)
  show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
  list_display = ('title', 'instructor', 'category', 'difficulty', 'price', 'is_published', 'thumbnail_preview')
  list_filter = ('category', 'difficulty', 'is_published', 'created_at')
  search_fields = ('title', 'short_description')
  readonly_fields = ('slug', 'average_rating', 'created_at', 'updated_at', 'thumbnail_preview')
  filter_horizontal = ('students',)
  inlines = [LessonInline]

  fieldsets = (
    (None, {
      'fields': ('title', 'slug', 'instructor', 'category')
    }),
    ('Content', {
      'fields': ('short_description', 'full_description', 'thumbnail', 'thumbnail_preview')
    }),
    ('Details', {
      'fields': ('difficulty', 'price', 'duration_hours', 'students')
    }),
    ('Status', {
      'fields': ('is_published', 'average_rating')
    }),
    ('Dates', {
      'fields': ('created_at', 'updated_at')
    }),
  )

  def thumbnail_preview(self, obj):
    if obj.thumbnail:
      return format_html('<img src="{}" style="max-height: 100px;"/>', obj.thumbnail.url)
    return "-"

  thumbnail_preview.short_description = 'Preview'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
  list_display = ('title', 'course', 'order', 'content_type', 'duration_minutes')
  list_filter = ('content_type', 'is_free')
  search_fields = ('title', 'content')
  inlines = [LessonResourceInline]
  autocomplete_fields = ['course']

  fieldsets = (
    (None, {
      'fields': ('course', 'order', 'title')
    }),
    ('Content', {
      'fields': ('content_type', 'content', 'duration_minutes')
    }),
    ('Access', {
      'fields': ('is_free',)
    }),
  )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
  list_display = ('student', 'course', 'enrolled_at', 'progress', 'completed_at')
  list_filter = ('course', 'enrolled_at')
  search_fields = ('student__username', 'course__title')
  readonly_fields = ('enrolled_at',)
  autocomplete_fields = ['student', 'course']

  fieldsets = (
    (None, {
      'fields': ('student', 'course')
    }),
    ('Progress', {
      'fields': ('progress', 'completed_at')
    }),
    ('Dates', {
      'fields': ('enrolled_at',)
    }),
  )


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
  list_display = ('student', 'course', 'rating', 'created_at')
  list_filter = ('rating', 'created_at')
  search_fields = ('comment', 'student__username', 'course__title')
  readonly_fields = ('created_at', 'updated_at')
  autocomplete_fields = ['student', 'course']

  fieldsets = (
    (None, {
      'fields': ('student', 'course')
    }),
    ('Review', {
      'fields': ('rating', 'comment')
    }),
    ('Dates', {
      'fields': ('created_at', 'updated_at')
    }),
  )