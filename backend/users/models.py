from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, URLValidator, EmailValidator
from django.db import models
import re  

def validate_twitter_handle(value):
    if value and not re.fullmatch(r'^[A-Za-z0-9_]+$', value):
        raise ValidationError('Twitter handle can only contain letters, numbers, and underscores.')

def validate_phone_number(value):
    phone_validator = RegexValidator(
        regex=r'^\+?\d{7,15}$',
        message='Enter a valid phone number, e.g. +1234567890'
    )
    phone_validator(value)

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        INSTRUCTOR = 'instructor', 'Instructor'
        ADMIN = 'admin', 'Admin'

    email = models.EmailField('email address', unique=True, validators=[EmailValidator()])

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        db_index=True,
    )

    bio = models.TextField(max_length=500, blank=True)

    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True
    )

    date_of_birth = models.DateField(blank=True, null=True)

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_phone_number],
        help_text='Phone number with country code, e.g. +1234567890',
    )

    website = models.URLField(blank=True, null=True, validators=[URLValidator()])

    twitter_handle = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[validate_twitter_handle],
        help_text='Twitter username without @. Allowed characters: letters, numbers, and underscores.',
    )

    linkedin_profile = models.URLField(blank=True, null=True, validators=[URLValidator()])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_instructor(self):
        return self.role == self.Role.INSTRUCTOR

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN