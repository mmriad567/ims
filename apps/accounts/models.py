from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that uses email instead of username for login."""

    class Role(models.TextChoices):
        # Administrator role with full system access.
        ADMIN = 'admin', 'Admin'
        # Teacher role for academic staff.
        TEACHER = 'teacher', 'Teacher'
        # Student role for learners.
        STUDENT = 'student', 'Student'

    # Unique email address used as the login identifier.
    email = models.EmailField(unique=True)
    # Human-readable display name for the user.
    full_name = models.CharField(max_length=150)
    # Role that controls what the user can access.
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    # Whether the account is allowed to log in.
    is_active = models.BooleanField(default=True)
    # Whether the user can access the Django admin site.
    is_staff = models.BooleanField(default=False)
    # Timestamp recorded when the account is created.
    date_joined = models.DateTimeField(default=timezone.now)

    # Attach the custom manager that understands email-based users.
    objects = UserManager()

    # Use email as the unique login field.
    USERNAME_FIELD = 'email'
    # Require a full name when creating users via CLI prompts.
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        # Return users sorted by email by default.
        ordering = ['email']
        # Enforce case-insensitive uniqueness at the database level.
        constraints = [
            models.UniqueConstraint(Lower('email'), name='unique_lower_email'),
        ]

    def __str__(self):
        # Show the email as the readable representation.
        return self.email

    def save(self, *args, **kwargs):
        # Normalize the email to lowercase before every save.
        if self.email:
            # Lowercase to keep storage and lookups consistent.
            self.email = self.email.lower()
        # Continue with the standard save logic.
        super().save(*args, **kwargs)
