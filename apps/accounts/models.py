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
        # Lowercase outside the manager too, so case cannot bypass uniqueness.
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)
