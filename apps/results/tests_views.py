from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User, StudentProfile, TeacherProfile
from apps.academics.models import Department, Semester, Section, Subject

from .models import Exam, Mark


class ResultViewsTest(TestCase):
    """Tests for teacher mark entry and student result views."""

    def setUp(self):
        """Create teacher, student, academic data, an exam and a mark."""
        self.department = Department.objects.create(name='Computer', code='CMT')
        self.semester = Semester.objects.create(
            number=6, department=self.department
        )
        self.section = Section.objects.create(
            name='A', semester=self.semester, shift='1st'
        )
        self.teacher_user = User.objects.create_user(
            email='teacher@example.com', full_name='Teacher One',
            role='teacher', password='test123',
        )
        self.teacher_profile = TeacherProfile.objects.create(
            user=self.teacher_user, department=self.department,
            designation='instructor',
        )
        self.student_user = User.objects.create_user(
            email='student@example.com', full_name='Student One',
            role='student', password='test123',
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user, roll_no='R001', registration_no='REG-R001',
            section=self.section, session='2025-2026',
        )
        self.subject = Subject.objects.create(
            name='Mathematics', code='MAT101', semester=self.semester,
        )
        self.subject.teachers.add(self.teacher_profile)
        self.exam = Exam.objects.create(
            name='Final 2026', exam_type='final', subject=self.subject,
            section=self.section, date=date(2026, 1, 20), total_marks=100,
        )
        self.mark = Mark.objects.create(
            exam=self.exam, student=self.student_profile, marks_obtained=85,
        )

    def test_exam_list_requires_teacher_role(self):
        """Students must receive 403 on the teacher exam list."""
        self.client.login(username='student@example.com', password='test123')
        response = self.client.get(reverse('results:exam_list'))
        self.assertEqual(response.status_code, 403)

    def test_exam_list_shows_own_exams(self):
        """A teacher must see exams for their assigned subjects."""
        self.client.login(username='teacher@example.com', password='test123')
        response = self.client.get(reverse('results:exam_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.exam.name)

    def test_marks_edit_get_shows_form(self):
        """The marks edit page must render its form template."""
        self.client.login(username='teacher@example.com', password='test123')
        response = self.client.get(
            reverse('results:exam_marks_edit', args=[self.exam.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'results/marks_edit.html')

    def test_marks_edit_post_updates_mark(self):
        """A valid formset POST must persist the new mark and redirect."""
        self.client.login(username='teacher@example.com', password='test123')
        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-id': self.mark.id,
            'form-0-marks_obtained': '90',
            'form-0-is_absent': '',
        }
        response = self.client.post(
            reverse('results:exam_marks_edit', args=[self.exam.id]), data
        )
        self.assertEqual(response.status_code, 302)
        self.mark.refresh_from_db()
        self.assertEqual(self.mark.marks_obtained, 90)

    def test_my_result_requires_student_role(self):
        """Teachers must receive 403 on the student result page."""
        self.client.login(username='teacher@example.com', password='test123')
        response = self.client.get(reverse('results:my_result'))
        self.assertEqual(response.status_code, 403)

    def test_my_result_shows_overall_gpa(self):
        """A student with 85 percent must see an overall GPA of 4.00."""
        self.client.login(username='student@example.com', password='test123')
        response = self.client.get(reverse('results:my_result'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '4.00')

    def test_my_result_detail_shows_exam(self):
        """The subject detail page must list the student's exams."""
        self.client.login(username='student@example.com', password='test123')
        response = self.client.get(
            reverse('results:my_result_detail', args=[self.subject.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.exam.name)
