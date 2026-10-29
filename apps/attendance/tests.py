from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.academics.models import Department, Section, Semester, Subject
from apps.accounts.models import StudentProfile, TeacherProfile

from .models import Attendance, ClassSession
from .services import calculate_attendance_summary, create_class_session_with_attendance

User = get_user_model()


def build_academic_setup():
    """Create the shared department, semester, section, subject and teacher."""
    department = Department.objects.create(name='Computer Science', code='CS')
    semester = Semester.objects.create(number=1, department=department)
    section = Section.objects.create(name='A', semester=semester, shift='1st')
    subject = Subject.objects.create(name='Programming', code='CS101', semester=semester)
    teacher_user = User.objects.create_user(
        email='teacher@example.com', full_name='Teacher One',
        role='teacher', password='test123',
    )
    teacher = TeacherProfile.objects.create(
        user=teacher_user, department=department, designation='instructor',
    )
    return department, semester, section, subject, teacher


def build_student(section, roll_no, is_active=True):
    """Create a student profile in the given section."""
    user = User.objects.create_user(
        email=f'{roll_no}@example.com', full_name=f'Student {roll_no}',
        role='student', password='test123',
    )
    return StudentProfile.objects.create(
        user=user, roll_no=roll_no, registration_no=f'REG-{roll_no}',
        section=section, session='2025-2026', is_active=is_active,
    )


class ClassSessionModelTest(TestCase):
    """Tests for ClassSession and Attendance model constraints."""

    def setUp(self):
        """Build academic data plus one teacher and one student."""
        _, _, self.section, self.subject, self.teacher = build_academic_setup()
        self.student = build_student(self.section, 'R001')

    def test_session_str_contains_subject_section_date_period(self):
        """Session string must include subject code, section, date and period."""
        session = ClassSession.objects.create(
            subject=self.subject, section=self.section, teacher=self.teacher,
            date=date(2026, 1, 5), period_no=3,
        )
        text = str(session)
        self.assertIn(self.subject.code, text)
        self.assertIn(str(self.section), text)
        self.assertIn('2026-01-05', text)
        self.assertIn('P3', text)

    def test_session_duplicate_raises_integrity_error(self):
        """Duplicate section/date/period session must raise IntegrityError."""
        ClassSession.objects.create(
            subject=self.subject, section=self.section, teacher=self.teacher,
            date=date(2026, 1, 5), period_no=1,
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ClassSession.objects.create(
                    subject=self.subject, section=self.section, teacher=self.teacher,
                    date=date(2026, 1, 5), period_no=1,
                )

    def test_attendance_duplicate_raises_integrity_error(self):
        """Duplicate session/student attendance must raise IntegrityError."""
        session = ClassSession.objects.create(
            subject=self.subject, section=self.section, teacher=self.teacher,
            date=date(2026, 1, 5), period_no=1,
        )
        Attendance.objects.create(session=session, student=self.student, status='present')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Attendance.objects.create(session=session, student=self.student, status='absent')


class CreateSessionServiceTest(TestCase):
    """Tests for create_class_session_with_attendance."""

    def setUp(self):
        """Build academic data with three active and one inactive student."""
        _, _, self.section, self.subject, self.teacher = build_academic_setup()
        self.active_students = [build_student(self.section, f'R00{i}') for i in (1, 2, 3)]
        self.inactive_student = build_student(self.section, 'R009', is_active=False)
        self.session_date = date(2026, 1, 5)

    def test_creates_session_row(self):
        """Service must create exactly one ClassSession."""
        create_class_session_with_attendance(
            self.subject, self.section, self.teacher, self.session_date, 2,
        )
        self.assertEqual(ClassSession.objects.count(), 1)

    def test_creates_one_attendance_per_active_student(self):
        """Service must create attendance only for the three active students."""
        create_class_session_with_attendance(
            self.subject, self.section, self.teacher, self.session_date, 2,
        )
        self.assertEqual(Attendance.objects.count(), 3)

    def test_new_attendance_defaults_to_absent(self):
        """Every generated attendance row must be absent."""
        create_class_session_with_attendance(
            self.subject, self.section, self.teacher, self.session_date, 2,
        )
        self.assertFalse(Attendance.objects.exclude(status='absent').exists())

    def test_duplicate_raises_validation_error(self):
        """Pre-check must raise ValidationError before writing anything."""
        create_class_session_with_attendance(
            self.subject, self.section, self.teacher, self.session_date, 2,
        )
        with self.assertRaises(ValidationError):
            create_class_session_with_attendance(
                self.subject, self.section, self.teacher, self.session_date, 2,
            )
        self.assertEqual(ClassSession.objects.count(), 1)

    def test_rollback_on_error(self):
        """A bulk_create failure must roll back the created session."""
        with patch(
            'apps.attendance.models.Attendance.objects.bulk_create',
            side_effect=Exception('boom'),
        ):
            with self.assertRaises(Exception):
                create_class_session_with_attendance(
                    self.subject, self.section, self.teacher, self.session_date, 2,
                )
        self.assertEqual(
            ClassSession.objects.filter(
                section=self.section, date=self.session_date, period_no=2,
            ).count(),
            0,
        )


class CalculateSummaryTest(TestCase):
    """Tests for calculate_attendance_summary."""

    def setUp(self):
        """Build academic data and a student for summary calculations."""
        _, self.semester, self.section, self.subject, self.teacher = build_academic_setup()
        self.student = build_student(self.section, 'R001')
        self.period = 0

    def _add_attendance(self, status, subject=None, section=None):
        """Create a session and an attendance row with the given status."""
        self.period += 1
        session = ClassSession.objects.create(
            subject=subject or self.subject, section=section or self.section,
            teacher=self.teacher, date=date(2026, 1, 5), period_no=self.period,
        )
        Attendance.objects.create(session=session, student=self.student, status=status)

    def test_all_present_returns_100_percent(self):
        """All present rows must give 100 percent."""
        self._add_attendance('present')
        self._add_attendance('present')
        summary = calculate_attendance_summary(self.student, self.subject)
        self.assertEqual(summary['percentage'], 100.0)

    def test_late_counted_as_present(self):
        """Late must count as attended, producing 75 percent."""
        self._add_attendance('present')
        self._add_attendance('present')
        self._add_attendance('late')
        self._add_attendance('absent')
        summary = calculate_attendance_summary(self.student, self.subject)
        self.assertEqual(summary['total'], 4)
        self.assertEqual(summary['late'], 1)
        self.assertEqual(summary['percentage'], 75.0)

    def test_zero_sessions_returns_zero_percent(self):
        """No attendance must return zero without dividing by zero."""
        summary = calculate_attendance_summary(self.student, self.subject)
        self.assertEqual(summary['total'], 0)
        self.assertEqual(summary['percentage'], 0.0)

    def test_subject_isolation(self):
        """Attendance from another subject must not be counted."""
        other_subject = Subject.objects.create(
            name='Mathematics', code='CS102', semester=self.semester,
        )
        self._add_attendance('present')
        self._add_attendance('present', subject=other_subject)
        summary = calculate_attendance_summary(self.student, self.subject)
        self.assertEqual(summary['total'], 1)
        self.assertEqual(summary['percentage'], 100.0)
