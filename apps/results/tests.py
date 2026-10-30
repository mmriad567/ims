from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import StudentProfile, TeacherProfile
from apps.academics.models import Department, Section, Semester, Subject

from .models import Exam, Mark
from .services import (
    calculate_exam_result,
    calculate_overall_result,
    calculate_subject_gpa,
    marks_to_grade,
)

User = get_user_model()


class GradeConversionTest(TestCase):
    """Boundary tests for the BTEB grade conversion table."""

    def test_80_percent_is_a_plus_4_00(self):
        """80 percent must map to A+ with 4.00 points."""
        self.assertEqual(marks_to_grade(80), ('A+', Decimal('4.00')))

    def test_79_percent_is_a_3_75(self):
        """79 percent must map to A with 3.75 points."""
        self.assertEqual(marks_to_grade(79), ('A', Decimal('3.75')))

    def test_40_percent_is_d_2_00(self):
        """40 percent must map to D with 2.00 points."""
        self.assertEqual(marks_to_grade(40), ('D', Decimal('2.00')))

    def test_39_percent_is_f_0_00(self):
        """39 percent must map to F with 0.00 points."""
        self.assertEqual(marks_to_grade(39), ('F', Decimal('0.00')))

    def test_0_percent_is_f_0_00(self):
        """0 percent must map to F with 0.00 points."""
        self.assertEqual(marks_to_grade(0), ('F', Decimal('0.00')))


class ExamResultTest(TestCase):
    """Tests for calculate_exam_result on a single exam."""

    def setUp(self):
        """Create teacher, student, academic data and a 100-mark exam."""
        teacher_user = User.objects.create_user(
            email='teacher@example.com', full_name='Teacher One',
            role='teacher', password='test123',
        )
        student_user = User.objects.create_user(
            email='student@example.com', full_name='Student One',
            role='student', password='test123',
        )
        self.department = Department.objects.create(name='Computer', code='CMT')
        self.semester = Semester.objects.create(
            number=6, department=self.department
        )
        self.section = Section.objects.create(
            name='A', semester=self.semester, shift='1st'
        )
        TeacherProfile.objects.create(
            user=teacher_user, department=self.department,
            designation='instructor',
        )
        self.student = StudentProfile.objects.create(
            user=student_user, roll_no='R001', registration_no='G001',
            section=self.section, session='2022-2023',
        )
        self.subject = Subject.objects.create(
            name='Mathematics', code='MAT101', semester=self.semester
        )
        self.exam = Exam.objects.create(
            name='Final Exam 2026', exam_type='final', subject=self.subject,
            section=self.section, date=date(2026, 1, 5), total_marks=100,
        )

    def test_absent_student_returns_f_with_zero(self):
        """An absent mark must yield F with zero obtained and grade points."""
        Mark.objects.create(
            exam=self.exam, student=self.student, marks_obtained=0,
            is_absent=True,
        )
        result = calculate_exam_result(self.exam, self.student)
        self.assertEqual(result['grade'], 'F')
        self.assertEqual(result['grade_point'], Decimal('0.00'))
        self.assertEqual(result['obtained'], Decimal('0'))
        self.assertTrue(result['is_absent'])

    def test_missing_mark_returns_none(self):
        """A student without a mark must return None."""
        self.assertIsNone(calculate_exam_result(self.exam, self.student))

    def test_75_marks_gives_a_3_75(self):
        """75 marks out of 100 must yield A with 3.75 points."""
        Mark.objects.create(
            exam=self.exam, student=self.student, marks_obtained=75,
        )
        result = calculate_exam_result(self.exam, self.student)
        self.assertEqual(result['percentage'], 75.0)
        self.assertEqual(result['grade'], 'A')
        self.assertEqual(result['grade_point'], Decimal('3.75'))


class SubjectGPATest(TestCase):
    """Tests for calculate_subject_gpa across multiple exams."""

    def setUp(self):
        """Create academic data plus final and midterm exams in one subject."""
        teacher_user = User.objects.create_user(
            email='teacher@example.com', full_name='Teacher One',
            role='teacher', password='test123',
        )
        student_user = User.objects.create_user(
            email='student@example.com', full_name='Student One',
            role='student', password='test123',
        )
        self.department = Department.objects.create(name='Computer', code='CMT')
        self.semester = Semester.objects.create(
            number=6, department=self.department
        )
        self.section = Section.objects.create(
            name='A', semester=self.semester, shift='1st'
        )
        TeacherProfile.objects.create(
            user=teacher_user, department=self.department,
            designation='instructor',
        )
        self.student = StudentProfile.objects.create(
            user=student_user, roll_no='R001', registration_no='G001',
            section=self.section, session='2022-2023',
        )
        self.subject = Subject.objects.create(
            name='Mathematics', code='MAT101', semester=self.semester
        )
        self.final = Exam.objects.create(
            name='Final Exam 2026', exam_type='final', subject=self.subject,
            section=self.section, date=date(2026, 1, 5), total_marks=100,
        )
        self.midterm = Exam.objects.create(
            name='Midterm Exam 2026', exam_type='midterm', subject=self.subject,
            section=self.section, date=date(2025, 10, 5), total_marks=100,
        )

    def test_two_exams_averaged(self):
        """A+ and A exams must average to a 3.88 subject GPA."""
        Mark.objects.create(
            exam=self.final, student=self.student, marks_obtained=100,
        )
        Mark.objects.create(
            exam=self.midterm, student=self.student, marks_obtained=75,
        )
        result = calculate_subject_gpa(self.student, self.subject)
        self.assertEqual(result['gpa'], Decimal('3.88'))
        self.assertFalse(result['has_fail'])

    def test_any_f_exam_makes_subject_gpa_zero(self):
        """A single failing exam must force the subject GPA to zero."""
        Mark.objects.create(
            exam=self.final, student=self.student, marks_obtained=100,
        )
        Mark.objects.create(
            exam=self.midterm, student=self.student, marks_obtained=30,
        )
        result = calculate_subject_gpa(self.student, self.subject)
        self.assertEqual(result['gpa'], Decimal('0.00'))
        self.assertTrue(result['has_fail'])

    def test_no_exams_returns_none_gpa(self):
        """A subject without exams must return a None GPA."""
        other = Subject.objects.create(
            name='Physics', code='PHY101', semester=self.semester
        )
        result = calculate_subject_gpa(self.student, other)
        self.assertIsNone(result['gpa'])
        self.assertEqual(result['exams'], [])
        self.assertFalse(result['has_fail'])


class OverallResultTest(TestCase):
    """Tests for calculate_overall_result across a student's subjects."""

    def setUp(self):
        """Create a student with two subjects, each having one A+ exam."""
        student_user = User.objects.create_user(
            email='student@example.com', full_name='Student One',
            role='student', password='test123',
        )
        self.department = Department.objects.create(name='Computer', code='CMT')
        self.semester = Semester.objects.create(
            number=6, department=self.department
        )
        self.section = Section.objects.create(
            name='A', semester=self.semester, shift='1st'
        )
        self.student = StudentProfile.objects.create(
            user=student_user, roll_no='R001', registration_no='G001',
            section=self.section, session='2022-2023',
        )
        self.subject_one = Subject.objects.create(
            name='Mathematics', code='MAT101', semester=self.semester
        )
        self.subject_two = Subject.objects.create(
            name='Physics', code='PHY101', semester=self.semester
        )
        self.exam_one = Exam.objects.create(
            name='Final Exam 2026', exam_type='final', subject=self.subject_one,
            section=self.section, date=date(2026, 1, 5), total_marks=100,
        )
        self.exam_two = Exam.objects.create(
            name='Final Exam 2026', exam_type='final', subject=self.subject_two,
            section=self.section, date=date(2026, 1, 6), total_marks=100,
        )
        self.mark_one = Mark.objects.create(
            exam=self.exam_one, student=self.student, marks_obtained=90,
        )
        self.mark_two = Mark.objects.create(
            exam=self.exam_two, student=self.student, marks_obtained=90,
        )

    def test_overall_gpa_is_average_of_subjects(self):
        """Two A+ subjects must produce an overall GPA of 4.00."""
        result = calculate_overall_result(self.student)
        self.assertEqual(result['overall_gpa'], Decimal('4.00'))
        self.assertFalse(result['has_fail'])

    def test_one_subject_f_makes_overall_zero(self):
        """A failing subject must force the overall GPA to zero."""
        self.mark_two.marks_obtained = 30
        self.mark_two.save()
        result = calculate_overall_result(self.student)
        self.assertEqual(result['overall_gpa'], Decimal('0.00'))
        self.assertTrue(result['has_fail'])

    def test_no_graded_subjects_returns_none(self):
        """Deleting all marks must return a None overall GPA."""
        Mark.objects.all().delete()
        result = calculate_overall_result(self.student)
        self.assertIsNone(result['overall_gpa'])
        self.assertFalse(result['has_fail'])
