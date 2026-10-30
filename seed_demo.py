import os
import django
from datetime import date, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import transaction
from apps.accounts.models import User, StudentProfile, TeacherProfile
from apps.academics.models import Department, Semester, Section, Subject
from apps.attendance.models import ClassSession, Attendance
from apps.results.models import Exam, Mark


def run_seed():
    """Populate the database with demo data for presentation."""
    print("Starting demo data generation...")

    with transaction.atomic():
        cmt, _ = Department.objects.get_or_create(code='CMT', defaults={'name': 'Computer Science & Technology'})

        cmt_sem6, _ = Semester.objects.get_or_create(department=cmt, number=6)

        cmt_sec_a, _ = Section.objects.get_or_create(semester=cmt_sem6, name='A', shift='1st')

        teachers_data = [
            ('karim@magura.com', 'Karim Ahmed', 'instructor'),
            ('rahim@magura.com', 'Rahim Uddin', 'lecturer'),
            ('jamal@magura.com', 'Jamal Hossain', 'junior_instructor')
        ]
        teacher_profiles = []
        for email, name, desig in teachers_data:
            u, created = User.objects.get_or_create(email=email, defaults={'full_name': name, 'role': 'teacher'})
            if created:
                u.set_password('password123')
                u.save()
            t, _ = TeacherProfile.objects.get_or_create(user=u, defaults={'department': cmt, 'designation': desig})
            teacher_profiles.append(t)

        dbms, _ = Subject.objects.get_or_create(code='28561', defaults={'name': 'Database Management System', 'semester': cmt_sem6, 'subject_type': 'theory'})
        dbms.teachers.add(teacher_profiles[0])

        network, _ = Subject.objects.get_or_create(code='28562', defaults={'name': 'Computer Networking', 'semester': cmt_sem6, 'subject_type': 'theory'})
        network.teachers.add(teacher_profiles[1])

        iot, _ = Subject.objects.get_or_create(code='28563', defaults={'name': 'Sensor & IoT System', 'semester': cmt_sem6, 'subject_type': 'theory'})
        iot.teachers.add(teacher_profiles[2])

        dbms_p, _ = Subject.objects.get_or_create(code='28561P', defaults={'name': 'Database Management System (Practical)', 'semester': cmt_sem6, 'subject_type': 'practical'})
        dbms_p.teachers.add(teacher_profiles[0])

        students_data = [
            ('Rahim', '123456'), ('Karim', '123457'), ('Salam', '123458'),
            ('Barkat', '123459'), ('Nusrat', '123460'), ('Fatema', '123461'),
            ('Hasan', '123462'), ('Jannat', '123463'), ('Sabbir', '123464'), ('Tania', '123465')
        ]
        students = []
        for name, roll in students_data:
            email = f"{roll}@student.magura.com"
            u, created = User.objects.get_or_create(email=email, defaults={'full_name': name, 'role': 'student'})
            if created:
                u.set_password('password123')
                u.save()
            s, _ = StudentProfile.objects.get_or_create(user=u, defaults={'roll_no': roll, 'registration_no': f'G{roll}', 'section': cmt_sec_a, 'session': '2022-2023'})
            students.append(s)

        print("Creating attendance sessions...")
        for i in range(10):
            s_date = date.today() - timedelta(days=15 - i)
            session, created = ClassSession.objects.get_or_create(
                subject=dbms, section=cmt_sec_a, teacher=teacher_profiles[0], date=s_date, period_no=1
            )
            if created:
                for s in students:
                    r = random.random()
                    status = 'present' if r < 0.7 else ('late' if r < 0.8 else 'absent')
                    Attendance.objects.create(session=session, student=s, status=status)

        print("Creating exam and marks...")
        exam, _ = Exam.objects.get_or_create(
            name='Midterm Exam 2026', exam_type='midterm', subject=dbms, section=cmt_sec_a, date=date.today() - timedelta(days=5), total_marks=100
        )
        for s in students:
            marks = round(random.uniform(45, 95), 2)
            Mark.objects.get_or_create(exam=exam, student=s, defaults={'marks_obtained': marks})

    print("=====================================")
    print("Successfully seeded demo data!")
    print("Teacher Login: karim@magura.com / password123")
    print("Student Login: 123456@student.magura.com / password123")
    print("=====================================")


if __name__ == '__main__':
    run_seed()
