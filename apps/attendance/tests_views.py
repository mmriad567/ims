from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User, StudentProfile, TeacherProfile
from apps.academics.models import Department, Semester, Section, Subject

from .models import ClassSession, Attendance
from .services import create_class_session_with_attendance


class AttendanceViewsTest(TestCase):
    """Tests for teacher and student attendance views."""

    def setUp(self):
        """Create teacher, student and one pre-populated class session."""
        self.department = Department.objects.create(name='Computer Science', code='CS')
        self.semester = Semester.objects.create(number=1, department=self.department)
        self.section = Section.objects.create(
            name='A', semester=self.semester, shift='1st',
        )

        self.teacher_user = User.objects.create_user(
            email='teacher@example.com', full_name='Teacher One',
            role='teacher', password='test123',
        )
        self.teacher_profile = TeacherProfile.objects.create(
            user=self.teacher_user, department=self.department, designation='instructor',
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
            name='Programming', code='CS101', semester=self.semester,
        )
        self.subject.teachers.add(self.teacher_profile)

        self.session = create_class_session_with_attendance(
            self.subject, self.section, self.teacher_profile, date(2026, 1, 15), 1,
        )

    def test_subject_list_requires_teacher_role(self):
        """Students must receive 403 on the teacher subject list."""
        self.client.login(username='student@example.com', password='test123')
        response = self.client.get(reverse('attendance:subject_list'))
        self.assertEqual(response.status_code, 403)

    def test_subject_list_shows_only_own_subjects(self):
        """A teacher must only see subjects assigned to them."""
        other_user = User.objects.create_user(
            email='other@example.com', full_name='Other Teacher',
            role='teacher', password='test123',
        )
        other_profile = TeacherProfile.objects.create(
            user=other_user, department=self.department, designation='lecturer',
        )
        other_subject = Subject.objects.create(
            name='Mathematics', code='CS102', semester=self.semester,
        )
        other_subject.teachers.add(other_profile)

        self.client.login(username='teacher@example.com', password='test123')
        response = self.client.get(reverse('attendance:subject_list'))
        self.assertContains(response, self.subject.code)
        self.assertNotContains(response, other_subject.code)

    def test_session_create_get_shows_form(self):
        """Session create page must render its template."""
        self.client.login(username='teacher@example.com', password='test123')
        response = self.client.get(
            reverse('attendance:session_create', args=[self.subject.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/session_create.html')

    def test_session_create_post_creates_session_and_redirects(self):
        """A valid POST must create a session and redirect to take attendance."""
        self.client.login(username='teacher@example.com', password='test123')
        response = self.client.post(
            reverse('attendance:session_create', args=[self.subject.id]),
            {'section': self.section.id, 'date': '2026-01-16', 'period_no': '2'},
        )
        self.assertEqual(response.status_code, 302)
        session = ClassSession.objects.get(date=date(2026, 1, 16), period_no=2)
        self.assertEqual(
            response.url, reverse('attendance:take', args=[session.id])
        )

    def test_session_create_duplicate_shows_error(self):
        """A duplicate session POST must show the already exists error."""
        self.client.login(username='teacher@example.com', password='test123')
        url = reverse('attendance:session_create', args=[self.subject.id])
        payload = {'section': self.section.id, 'date': '2026-01-17', 'period_no': '3'}
        self.client.post(url, payload)
        response = self.client.post(url, payload)
        self.assertContains(response, 'already exists')

    def test_take_attendance_requires_ownership(self):
        """A teacher must not access another teacher's session."""
        other_user = User.objects.create_user(
            email='other@example.com', full_name='Other Teacher',
            role='teacher', password='test123',
        )
        other_profile = TeacherProfile.objects.create(
            user=other_user, department=self.department, designation='lecturer',
        )
        other_session = ClassSession.objects.create(
            subject=self.subject, section=self.section, teacher=other_profile,
            date=date(2026, 2, 1), period_no=1,
        )
        self.client.login(username='teacher@example.com', password='test123')
        response = self.client.get(
            reverse('attendance:take', args=[other_session.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_toggle_attendance_updates_status(self):
        """Toggling must persist the status and return the updated button."""
        attendance = Attendance.objects.get(
            session=self.session, student=self.student_profile,
        )
        self.client.login(username='teacher@example.com', password='test123')
        response = self.client.post(
            reverse('attendance:toggle', args=[attendance.id]),
            {'status': 'present'},
        )
        attendance.refresh_from_db()
        self.assertEqual(attendance.status, 'present')
        self.assertContains(response, 'bg-green-600')

    def test_student_my_attendance_shows_only_own_records(self):
        """The student summary page must list their semester subjects."""
        self.client.login(username='student@example.com', password='test123')
        response = self.client.get(reverse('attendance:my_attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.subject.code)

    def test_student_my_attendance_detail_shows_session_date(self):
        """The detail page must include the session date."""
        self.client.login(username='student@example.com', password='test123')
        response = self.client.get(
            reverse('attendance:my_attendance_detail', args=[self.subject.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.session.date.strftime('%Y-%m-%d'))

    def test_student_can_download_attendance_pdf(self):
        """The student must receive a valid PDF attendance report."""
        self.client.login(username='student@example.com', password='test123')
        response = self.client.get(
            reverse('attendance:my_attendance_pdf', args=[self.subject.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))
