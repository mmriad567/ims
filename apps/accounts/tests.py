from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

User = get_user_model()


class UserManagerTests(TestCase):
    """Tests for the custom email-based user manager and model."""

    def test_create_user_success(self):
        # Create a regular student account through the manager.
        user = User.objects.create_user(
            email='student@example.com',
            full_name='Student One',
            role='student',
            password='secret123',
        )
        # Verify the requested role is stored on the user.
        self.assertEqual(user.role, 'student')
        # Verify regular users are not staff members.
        self.assertFalse(user.is_staff)
        # Verify regular users are not superusers.
        self.assertFalse(user.is_superuser)
        # Verify the raw password is not stored in the password field.
        self.assertNotEqual(user.password, 'secret123')
        # Verify the stored hash matches the original password.
        self.assertTrue(user.check_password('secret123'))

    def test_email_lowercased_on_create(self):
        # Create a user with mixed-case email input.
        user = User.objects.create_user(
            email='TEST@Example.COM',
            full_name='Case Test',
            role='teacher',
            password='secret123',
        )
        # Verify the stored email is fully lowercase.
        self.assertEqual(user.email, 'test@example.com')

    def test_duplicate_email_raises(self):
        # Create the first account with a given email.
        User.objects.create_user(
            email='duplicate@example.com',
            full_name='First User',
            role='student',
            password='secret123',
        )
        # Attempt to create a second account with the same email.
        with self.assertRaises(IntegrityError):
            # Wrap the failing insert in an atomic block to keep the test transaction usable.
            with transaction.atomic():
                # This insert must violate the unique email constraint.
                User.objects.create_user(
                    email='duplicate@example.com',
                    full_name='Second User',
                    role='student',
                    password='secret123',
                )

    def test_create_superuser_sets_admin_and_flags(self):
        # Create a superuser through the manager.
        user = User.objects.create_superuser(
            email='admin@example.com',
            full_name='Admin User',
            password='secret123',
        )
        # Verify superusers always receive the admin role.
        self.assertEqual(user.role, 'admin')
        # Verify superusers are marked as staff.
        self.assertTrue(user.is_staff)
        # Verify superusers are marked as superusers.
        self.assertTrue(user.is_superuser)

    def test_get_by_natural_key_case_insensitive(self):
        # Create a user with a lowercase email.
        user = User.objects.create_user(
            email='natural@example.com',
            full_name='Natural Key',
            role='student',
            password='secret123',
        )
        # Look the user up using a different letter case.
        found = User.objects.get_by_natural_key('NATURAL@EXAMPLE.COM')
        # Verify the lookup returns the same user record.
        self.assertEqual(found.pk, user.pk)
