from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST

from apps.core.decorators import role_required
from apps.academics.models import Subject
from .models import ClassSession, Attendance
from .forms import ClassSessionForm
from .services import create_class_session_with_attendance, calculate_attendance_summary


@login_required
@role_required('teacher')
def subject_list(request):
    """Show subjects assigned to the logged-in teacher."""
    subjects = Subject.objects.filter(
        teachers=request.user.teacher_profile
    ).select_related('semester__department').order_by('code')
    return render(request, 'attendance/subject_list.html', {'subjects': subjects})


@login_required
@role_required('teacher')
def session_create(request, subject_id):
    """Create a new class session for a subject; pre-populates attendance."""
    subject = get_object_or_404(
        Subject, id=subject_id, teachers=request.user.teacher_profile
    )
    if request.method == 'POST':
        form = ClassSessionForm(request.POST, subject=subject)
        if form.is_valid():
            try:
                session = create_class_session_with_attendance(
                    subject=subject,
                    section=form.cleaned_data['section'],
                    teacher=request.user.teacher_profile,
                    date=form.cleaned_data['date'],
                    period_no=int(form.cleaned_data['period_no']),
                )
                return redirect('attendance:take', session_id=session.id)
            except ValidationError as e:
                form.add_error(None, e.messages[0] if hasattr(e, 'messages') else str(e))
    else:
        form = ClassSessionForm(subject=subject)
    return render(request, 'attendance/session_create.html', {
        'subject': subject, 'form': form,
    })


@login_required
@role_required('teacher')
def take_attendance(request, session_id):
    """Render the attendance marking page for a session."""
    session = get_object_or_404(
        ClassSession, id=session_id, teacher=request.user.teacher_profile
    )
    attendances = session.attendances.select_related(
        'student__user'
    ).order_by('student__roll_no')
    return render(request, 'attendance/take.html', {
        'session': session, 'attendances': attendances,
    })


@login_required
@role_required('teacher')
@require_POST
def toggle_attendance(request, attendance_id):
    """Update one attendance status; returns HTMX partial."""
    att = get_object_or_404(
        Attendance, id=attendance_id,
        session__teacher=request.user.teacher_profile,
    )
    status = request.POST.get('status')
    if status in dict(Attendance.STATUS_CHOICES):
        att.status = status
        att.save(update_fields=['status'])
    return render(request, 'attendance/_attendance_row.html', {'att': att})


@login_required
@role_required('student')
def my_attendance(request):
    """Show attendance summary for all subjects in the student's semester."""
    student = request.user.student_profile
    subjects = Subject.objects.filter(
        semester=student.section.semester
    ).order_by('code')
    summaries = [calculate_attendance_summary(student, s) for s in subjects]
    return render(request, 'attendance/my_attendance.html', {
        'summaries': summaries, 'student': student,
    })


@login_required
@role_required('student')
def my_attendance_detail(request, subject_id):
    """Show detailed attendance records for one subject."""
    student = request.user.student_profile
    subject = get_object_or_404(
        Subject, id=subject_id, semester=student.section.semester
    )
    attendances = Attendance.objects.filter(
        student=student, session__subject=subject
    ).select_related('session').order_by('-session__date', '-session__period_no')
    summary = calculate_attendance_summary(student, subject)
    return render(request, 'attendance/my_attendance_detail.html', {
        'subject': subject, 'attendances': attendances, 'summary': summary,
    })
