from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Manager for the custom email-based User model."""

    def _create_user(self, email, full_name, role, password=None, **extra_fields):
        """Create and persist a user after validating the email and role."""
        # Reject blank emails so the login identifier is always usable.
        if not email:
            raise ValueError('The email field must be set.')
        # Guard against invalid roles reaching the database.
        if role not in ('admin', 'teacher', 'student'):
            raise ValueError("Role must be 'admin', 'teacher', or 'student'.")

        email = email.lower()
        user = self.model(email=email, full_name=full_name, role=role, **extra_fields)
        # set_password hashes the password; assigning it directly would store plaintext.
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, full_name, role, password=None, **extra_fields):
        """Create a regular user with staff and superuser privileges forced off."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        # Force the flags off even if a caller supplies them.
        extra_fields['is_staff'] = False
        extra_fields['is_superuser'] = False
        return self._create_user(email, full_name, role, password, **extra_fields)

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        """Create an admin superuser, requiring both privilege flags to be true."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # An inconsistent superuser would be unusable, so reject it early.
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, full_name, 'admin', password, **extra_fields)

    def get_by_natural_key(self, email):
        """Look up a user by email, ignoring letter case."""
        return self.get(email=email.lower())
