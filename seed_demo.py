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
    """Populate the database with demo data for presentation, clearing old data first."""
    print("Starting demo data generation...")

    with transaction.atomic():
        print("1. Clearing old demo data...")
        Mark.objects.all().delete()
        Exam.objects.all().delete()
        Attendance.objects.all().delete()
        ClassSession.objects.all().delete()
        Subject.objects.all().delete()
        StudentProfile.objects.all().delete()
        TeacherProfile.objects.all().delete()
        Section.objects.all().delete()
        Semester.objects.all().delete()
        Department.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        print("2. Creating Departments and Sections...")
        cmt, _ = Department.objects.get_or_create(code='CMT', defaults={'name': 'Computer Science & Technology'})
        cmt_sem6, _ = Semester.objects.get_or_create(department=cmt, number=6)
        cmt_sec_a, _ = Section.objects.get_or_create(semester=cmt_sem6, name='A', shift='1st')

        print("3. Creating Teachers...")
        teachers_data = [
            ('karim@magura.com', 'Karim Ahmed', 'instructor'),
            ('rahim@magura.com', 'Rahim Uddin', 'lecturer'),
            ('jamal@magura.com', 'Jamal Hossain', 'junior_instructor')
        ]
        teacher_profiles = []
        for email, name, desig in teachers_data:
            u = User.objects.create_user(email=email, full_name=name, role='teacher', password='password123')
            t, _ = TeacherProfile.objects.get_or_create(user=u, defaults={'department': cmt, 'designation': desig})
            teacher_profiles.append(t)

        print("4. Creating Subjects...")
        dbms, _ = Subject.objects.get_or_create(code='28561', defaults={'name': 'Database Management System', 'semester': cmt_sem6, 'subject_type': 'theory'})
        dbms.teachers.add(teacher_profiles[0])

        network, _ = Subject.objects.get_or_create(code='28562', defaults={'name': 'Computer Networking', 'semester': cmt_sem6, 'subject_type': 'theory'})
        network.teachers.add(teacher_profiles[1])

        iot, _ = Subject.objects.get_or_create(code='28563', defaults={'name': 'Sensor & IoT System', 'semester': cmt_sem6, 'subject_type': 'theory'})
        iot.teachers.add(teacher_profiles[2])

        dbms_p, _ = Subject.objects.get_or_create(code='28561P', defaults={'name': 'Database Management System (Practical)', 'semester': cmt_sem6, 'subject_type': 'practical'})
        dbms_p.teachers.add(teacher_profiles[0])

        print("5. Creating Students...")
        students_data = [
            ('Rahim', '123456'), ('Karim', '123457'), ('Salam', '123458'),
            ('Barkat', '123459'), ('Nusrat', '123460'), ('Fatema', '123461'),
            ('Hasan', '123462'), ('Jannat', '123463'), ('Sabbir', '123464'), ('Tania', '123465')
        ]
        students = []
        for name, roll in students_data:
            email = f"{roll}@student.magura.com"
            u = User.objects.create_user(email=email, full_name=name, role='student', password='password123')
            s, _ = StudentProfile.objects.get_or_create(user=u, defaults={'roll_no': roll, 'registration_no': f'G{roll}', 'section': cmt_sec_a, 'session': '2022-2023'})
            students.append(s)

        print("6. Creating Attendance for all subjects...")
        subjects_teachers = [
            (dbms, teacher_profiles[0]),
            (network, teacher_profiles[1]),
            (iot, teacher_profiles[2]),
            (dbms_p, teacher_profiles[0])
        ]

        for i in range(5):
            s_date = date.today() - timedelta(days=10 - i)
            periods = random.sample(range(1, 6), len(subjects_teachers))
            for (subject, teacher), period_no in zip(subjects_teachers, periods):
                session, created = ClassSession.objects.get_or_create(
                    subject=subject, section=cmt_sec_a, teacher=teacher, date=s_date, period_no=period_no
                )
                if created:
                    for s in students:
                        r = random.random()
                        status = 'present' if r < 0.75 else ('late' if r < 0.85 else 'absent')
                        Attendance.objects.create(session=session, student=s, status=status)

        print("7. Creating Exams and Marks for all subjects...")
        for subject, _ in subjects_teachers:
            exam, _ = Exam.objects.get_or_create(
                name=f'Midterm Exam 2026 - {subject.code}',
                exam_type='midterm',
                subject=subject,
                section=cmt_sec_a,
                date=date.today() - timedelta(days=5),
                total_marks=100
            )
            for s in students:
                marks = round(random.uniform(40, 98), 2)
                Mark.objects.get_or_create(exam=exam, student=s, defaults={'marks_obtained': marks})

    print("=====================================")
    print("Successfully seeded demo data for ALL subjects!")
    print("Teacher Login: karim@magura.com / password123")
    print("Student Login: 123456@student.magura.com / password123")
    print("=====================================")


if __name__ == '__main__':
    run_seed()
