from django.contrib import admin

from .models import Attendance, ClassSession


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    """Admin for ClassSession."""

    list_display = ['subject', 'section', 'teacher', 'date', 'period_no']
    list_filter = ['date', 'subject__semester__department', 'section__shift']
    search_fields = ['subject__code', 'subject__name', 'section__name']
    autocomplete_fields = ['subject', 'section', 'teacher']
    date_hierarchy = 'date'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin for Attendance."""

    list_display = ['session', 'student', 'status', 'marked_at']
    list_filter = ['status', 'session__date']
    search_fields = ['student__roll_no', 'student__user__full_name']
    autocomplete_fields = ['session', 'student']
