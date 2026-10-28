from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that authenticates by email instead of username."""

    class Role(models.TextChoices):
        """Roles available to a user account."""

        ADMIN = 'admin', 'Admin'
        TEACHER = 'teacher', 'Teacher'
        STUDENT = 'student', 'Student'

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        """Default ordering and case-insensitive email uniqueness."""

        ordering = ['email']
        constraints = [
            models.UniqueConstraint(Lower('email'), name='unique_lower_email'),
        ]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        """Normalize the email to lowercase before saving."""
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)


class StudentProfile(models.Model):
    """Academic profile linked to a student user."""

    user = models.OneToOneField(
        'accounts.User', on_delete=models.CASCADE, related_name='student_profile'
    )
    roll_no = models.CharField(max_length=20, unique=True)
    registration_no = models.CharField(max_length=20, unique=True)
    section = models.ForeignKey(
        'academics.Section', on_delete=models.PROTECT, related_name='students'
    )
    session = models.CharField(max_length=9)
    phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['roll_no']

    def __str__(self):
        return f"{self.roll_no} - {self.user.full_name}"


class TeacherProfile(models.Model):
    """Academic profile linked to a teacher user."""

    class Designation(models.TextChoices):
        """Designations available to a teacher."""

        INSTRUCTOR = 'instructor', 'Instructor'
        JUNIOR_INSTRUCTOR = 'junior_instructor', 'Junior Instructor'
        LECTURER = 'lecturer', 'Lecturer'
        CHIEF_INSTRUCTOR = 'chief_instructor', 'Chief Instructor'

    user = models.OneToOneField(
        'accounts.User', on_delete=models.CASCADE, related_name='teacher_profile'
    )
    department = models.ForeignKey(
        'academics.Department', on_delete=models.PROTECT, related_name='teachers'
    )
    designation = models.CharField(max_length=30, choices=Designation.choices)
    phone = models.CharField(max_length=15, blank=True)

    class Meta:
        ordering = ['user__full_name']

    def __str__(self):
        return f"{self.user.full_name} ({self.get_designation_display()})"
