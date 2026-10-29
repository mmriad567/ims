from django.db import transaction
from django.core.exceptions import ValidationError

from .models import ClassSession, Attendance
from apps.accounts.models import StudentProfile


def create_class_session_with_attendance(subject, section, teacher, date, period_no):
    """Create session + pre-populate absent attendance for all active students."""
    if ClassSession.objects.filter(section=section, date=date, period_no=period_no).exists():
        raise ValidationError(f"A session already exists for {section} on {date} period {period_no}")
    with transaction.atomic():
        session = ClassSession.objects.create(
            subject=subject, section=section, teacher=teacher,
            date=date, period_no=period_no,
        )
        students = StudentProfile.objects.filter(section=section, is_active=True)
        Attendance.objects.bulk_create([
            Attendance(session=session, student=s, status='absent')
            for s in students
        ])
    return session


def calculate_attendance_summary(student, subject):
    """Return dict of total/present/late/absent/percentage for a student in a subject."""
    attendances = Attendance.objects.filter(session__subject=subject, student=student)
    total = attendances.count()
    present = attendances.filter(status='present').count()
    late = attendances.filter(status='late').count()
    absent = attendances.filter(status='absent').count()
    attended = present + late
    percentage = round(attended / total * 100, 2) if total else 0.0
    return {
        'subject': subject, 'total': total,
        'present': present, 'late': late, 'absent': absent,
        'percentage': percentage,
    }
