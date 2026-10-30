from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import modelformset_factory
from django import forms

from apps.core.decorators import role_required
from apps.academics.models import Subject
from apps.accounts.models import StudentProfile
from .models import Exam, Mark
from .services import calculate_subject_gpa, calculate_overall_result


class MarkForm(forms.ModelForm):
    """Form for a single student's mark in one exam."""

    class Meta:
        """Limit the form to score and absence fields."""

        model = Mark
        fields = ['marks_obtained', 'is_absent']
        widgets = {
            'marks_obtained': forms.NumberInput(
                attrs={
                    'class': 'w-24 border rounded px-2 py-1',
                    'step': '0.01',
                }
            ),
        }


MarkFormSet = modelformset_factory(
    Mark, form=MarkForm, extra=0, can_delete=False,
)


@login_required
@role_required('teacher')
def exam_list(request):
    """Show exams for subjects assigned to the teacher."""
    exams = Exam.objects.filter(
        subject__teachers=request.user.teacher_profile
    ).select_related('subject', 'section').order_by('-date')
    return render(request, 'results/exam_list.html', {'exams': exams})


@login_required
@role_required('teacher')
def exam_marks_edit(request, exam_id):
    """Enter or edit marks for all active students in an exam's section."""
    exam = get_object_or_404(
        Exam, id=exam_id, subject__teachers=request.user.teacher_profile
    )
    students = StudentProfile.objects.filter(
        section=exam.section, is_active=True
    ).order_by('roll_no')

    for s in students:
        Mark.objects.get_or_create(
            exam=exam, student=s,
            defaults={'marks_obtained': 0, 'is_absent': False},
        )

    queryset = Mark.objects.filter(exam=exam).select_related(
        'student__user'
    ).order_by('student__roll_no')

    if request.method == 'POST':
        formset = MarkFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            formset.save()
            return redirect('results:exam_marks_edit', exam_id=exam.id)
    else:
        formset = MarkFormSet(queryset=queryset)

    paired = list(zip(formset.forms, queryset))
    return render(request, 'results/marks_edit.html', {
        'exam': exam, 'formset': formset, 'paired': paired,
    })


@login_required
@role_required('student')
def my_result(request):
    """Show overall GPA and subject-wise breakdown for the logged-in student."""
    student = request.user.student_profile
    result = calculate_overall_result(student)
    return render(request, 'results/my_result.html', {
        'student': student, 'result': result,
    })


@login_required
@role_required('student')
def my_result_detail(request, subject_id):
    """Show exam-wise marks and GPA for one subject."""
    student = request.user.student_profile
    subject = get_object_or_404(
        Subject, id=subject_id, semester=student.section.semester
    )
    subject_result = calculate_subject_gpa(student, subject)
    return render(request, 'results/my_result_detail.html', {
        'student': student, 'subject': subject, 'result': subject_result,
    })
