from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.academics.models import Department, Section, Semester, Subject

from .models import StudentProfile, TeacherProfile

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


class ProfileTest(TestCase):
    """Tests for student and teacher profiles and subject assignment."""

    def setUp(self):
        """Create shared users and academic data."""

        self.user_student = User.objects.create_user(
            email='s@x.com', full_name='Stu Dent', role='student', password='x'
        )
        self.user_teacher = User.objects.create_user(
            email='t@x.com', full_name='Tea Cher', role='teacher', password='x'
        )
        self.dept = Department.objects.create(code='CMT', name='Computer')
        self.sem = Semester.objects.create(number=6, department=self.dept)
        self.section = Section.objects.create(
            name='A', semester=self.sem, shift='1st'
        )

    def test_student_profile_creates(self):
        """A student profile is persisted with its academic details."""

        StudentProfile.objects.create(
            user=self.user_student,
            roll_no='R001',
            registration_no='G001',
            section=self.section,
            session='2022-2023',
        )
        self.assertTrue(StudentProfile.objects.filter(roll_no='R001').exists())

    def test_student_roll_unique(self):
        """Duplicate roll numbers raise IntegrityError."""

        StudentProfile.objects.create(
            user=self.user_student,
            roll_no='R001',
            registration_no='G001',
            section=self.section,
            session='2022-2023',
        )
        other = User.objects.create_user(
            email='s2@x.com', full_name='Other Stu', role='student', password='x'
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                StudentProfile.objects.create(
                    user=other,
                    roll_no='R001',
                    registration_no='G002',
                    section=self.section,
                    session='2022-2023',
                )

    def test_teacher_profile_creates(self):
        """A teacher profile is persisted for the teacher user."""

        teacher = TeacherProfile.objects.create(
            user=self.user_teacher, department=self.dept, designation='instructor'
        )
        self.assertTrue(TeacherProfile.objects.filter(pk=teacher.pk).exists())

    def test_teacher_str_shows_designation(self):
        """Teacher profile string includes the designation label."""

        teacher = TeacherProfile.objects.create(
            user=self.user_teacher, department=self.dept, designation='instructor'
        )
        self.assertIn('Instructor', str(teacher))

    def test_subject_m2m_with_teacher(self):
        """A teacher assigned to a subject appears in its teachers set."""

        teacher = TeacherProfile.objects.create(
            user=self.user_teacher, department=self.dept, designation='instructor'
        )
        subject = Subject.objects.create(code='CMT101', name='Test', semester=self.sem)
        subject.teachers.add(teacher)
        self.assertIn(teacher, subject.teachers.all())
