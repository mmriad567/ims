from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from .models import Department, Section, Semester, Subject


class AcademicsModelTests(TestCase):
    """Tests for academics models."""

    def setUp(self):
        """Create shared department, semester, section, and subject data."""

        self.dept = Department.objects.create(
            code='CMT', name='Computer Science & Technology'
        )
        self.sem = Semester.objects.create(number=6, department=self.dept)
        self.section = Section.objects.create(
            name='A', semester=self.sem, shift='1st'
        )
        self.subject = Subject.objects.create(
            code='28561', name='DBMS', semester=self.sem, subject_type='theory'
        )

    def test_department_str(self):
        """Department string is code followed by name."""

        self.assertEqual(str(self.dept), 'CMT - Computer Science & Technology')

    def test_department_duplicate_code_raises(self):
        """Duplicate department code raises IntegrityError."""

        with self.assertRaises(IntegrityError):
            Department.objects.create(code='CMT', name='Another Department')

    def test_semester_duplicate_per_department_raises(self):
        """Duplicate semester number within a department raises IntegrityError."""

        with self.assertRaises(IntegrityError):
            Semester.objects.create(number=6, department=self.dept)

    def test_semester_number_validator_rejects_0(self):
        """Semester number 0 fails validation."""

        semester = Semester(number=0, department=self.dept)
        with self.assertRaises(ValidationError):
            semester.full_clean()

    def test_semester_number_validator_rejects_9(self):
        """Semester number 9 fails validation."""

        semester = Semester(number=9, department=self.dept)
        with self.assertRaises(ValidationError):
            semester.full_clean()

    def test_section_duplicate_raises(self):
        """Duplicate section name and shift within a semester raises IntegrityError."""

        with self.assertRaises(IntegrityError):
            Section.objects.create(name='A', semester=self.sem, shift='1st')

    def test_subject_duplicate_code_raises(self):
        """Duplicate subject code raises IntegrityError."""

        with self.assertRaises(IntegrityError):
            Subject.objects.create(
                code='28561', name='Another Subject', semester=self.sem
            )

    def test_subject_str(self):
        """Subject string is code followed by name."""

        self.assertEqual(str(self.subject), '28561 - DBMS')

    def test_section_str(self):
        """Section string includes semester, section name, and shift."""

        self.assertEqual(
            str(self.section),
            'CMT - Semester 6 - Section A (1st)',
        )

    def test_semester_str(self):
        """Semester string includes department code and number."""

        self.assertEqual(str(self.sem), 'CMT - Semester 6')
