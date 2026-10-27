from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Manager for the custom email-based User model."""

    def _create_user(self, email, full_name, role, password=None, **extra_fields):
        # Require an email address because it is the login identifier.
        if not email:
            # Reject blank emails with a clear error.
            raise ValueError('The email field must be set.')
        # Validate the role against the allowed role values.
        if role not in ('admin', 'teacher', 'student'):
            # Reject unsupported roles.
            raise ValueError("Role must be 'admin', 'teacher', or 'student'.")
        # Lowercase the email so lookups are case-insensitive.
        email = email.lower()
        # Build the user instance with the normalized email.
        user = self.model(email=email, full_name=full_name, role=role, **extra_fields)
        # Hash and store the password using Django's password hashing.
        user.set_password(password)
        # Persist the user to the database bound to this manager.
        user.save(using=self._db)
        # Return the newly created user instance.
        return user

    def create_user(self, email, full_name, role, password=None, **extra_fields):
        # Ensure regular users never get staff privileges.
        extra_fields.setdefault('is_staff', False)
        # Ensure regular users never get superuser privileges.
        extra_fields.setdefault('is_superuser', False)
        # Force staff status off even if a caller tries to pass it.
        extra_fields['is_staff'] = False
        # Force superuser status off even if a caller tries to pass it.
        extra_fields['is_superuser'] = False
        # Delegate creation to the shared internal method.
        return self._create_user(email, full_name, role, password, **extra_fields)

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        # Default superusers to staff status.
        extra_fields.setdefault('is_staff', True)
        # Default superusers to superuser status.
        extra_fields.setdefault('is_superuser', True)
        # Reject superusers that are not marked as staff.
        if extra_fields.get('is_staff') is not True:
            # Raise a clear error for invalid superuser flags.
            raise ValueError('Superuser must have is_staff=True.')
        # Reject superusers that are not marked as superuser.
        if extra_fields.get('is_superuser') is not True:
            # Raise a clear error for invalid superuser flags.
            raise ValueError('Superuser must have is_superuser=True.')
        # Create the superuser with the admin role.
        return self._create_user(email, full_name, 'admin', password, **extra_fields)

    def get_by_natural_key(self, email):
        # Lowercase the input so authentication is case-insensitive.
        return self.get(email=email.lower())
