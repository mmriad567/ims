from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class DashboardAccessTest(TestCase):
    """Tests for login, logout and role-based dashboard routing."""

    def setUp(self):
        """Create one user for each role."""
        self.admin_user = User.objects.create_user(
            email='a@x.com', full_name='Ad Min', role='admin', password='test123'
        )
        self.teacher_user = User.objects.create_user(
            email='t@x.com', full_name='Tea Cher', role='teacher', password='test123'
        )
        self.student_user = User.objects.create_user(
            email='s@x.com', full_name='Stu Dent', role='student', password='test123'
        )

    def test_login_page_loads(self):
        """Login page must render the login template."""
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_with_valid_email(self):
        """Valid credentials must redirect to the dashboard root."""
        response = self.client.post(
            '/login/', {'username': 'a@x.com', 'password': 'test123'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_login_with_wrong_password(self):
        """Wrong password must re-render the login form."""
        response = self.client.post(
            '/login/', {'username': 'a@x.com', 'password': 'wrongpass'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_dashboard_requires_login(self):
        """Anonymous dashboard access must redirect to login with next."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/?next=/')

    def test_admin_sees_admin_dashboard(self):
        """Admin users must see the admin dashboard."""
        self.client.login(username='a@x.com', password='test123')
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'dashboards/admin.html')

    def test_teacher_sees_teacher_dashboard(self):
        """Teacher users must see the teacher dashboard."""
        self.client.login(username='t@x.com', password='test123')
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'dashboards/teacher.html')

    def test_student_sees_student_dashboard(self):
        """Student users must see the student dashboard."""
        self.client.login(username='s@x.com', password='test123')
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'dashboards/student.html')
