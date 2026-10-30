from django.contrib import admin

from .models import Exam, Mark


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    """Admin for Exam."""

    list_display = ['name', 'exam_type', 'subject', 'section', 'date', 'total_marks']
    list_filter = ['exam_type', 'date', 'subject__semester__department']
    search_fields = ['name', 'subject__code', 'subject__name']
    autocomplete_fields = ['subject', 'section']
    date_hierarchy = 'date'


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    """Admin for Mark."""

    list_display = ['exam', 'student', 'marks_obtained', 'is_absent']
    list_filter = ['is_absent', 'exam__exam_type', 'exam__subject']
    search_fields = ['student__roll_no', 'student__user__full_name']
    autocomplete_fields = ['exam', 'student']
    list_editable = ['marks_obtained', 'is_absent']
