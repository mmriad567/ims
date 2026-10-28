from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

User = get_user_model()


class UserManagerTests(TestCase):
    """Tests for the custom email-based user manager and model."""

    def test_create_user_success(self):
        """A regular user must keep the requested role and remain non-staff."""
        user = User.objects.create_user(
            email='student@example.com',
            full_name='Student One',
            role='student',
            password='secret123',
        )
        self.assertEqual(user.role, 'student')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertNotEqual(user.password, 'secret123')
        self.assertTrue(user.check_password('secret123'))

    def test_email_lowercased_on_create(self):
        """Email must be lowercased on creation."""
        user = User.objects.create_user(
            email='TEST@Example.COM',
            full_name='Case Test',
            role='teacher',
            password='secret123',
        )
        self.assertEqual(user.email, 'test@example.com')

    def test_duplicate_email_raises(self):
        """Duplicate emails must violate the unique constraint."""
        User.objects.create_user(
            email='duplicate@example.com',
            full_name='First User',
            role='student',
            password='secret123',
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    email='duplicate@example.com',
                    full_name='Second User',
                    role='student',
                    password='secret123',
                )

    def test_create_superuser_sets_admin_and_flags(self):
        """A superuser must get the admin role and both privilege flags."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            full_name='Admin User',
            password='secret123',
        )
        self.assertEqual(user.role, 'admin')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_get_by_natural_key_case_insensitive(self):
        """Natural-key lookup must be case-insensitive."""
        user = User.objects.create_user(
            email='natural@example.com',
            full_name='Natural Key',
            role='student',
            password='secret123',
        )
        found = User.objects.get_by_natural_key('NATURAL@EXAMPLE.COM')
        self.assertEqual(found.pk, user.pk)
