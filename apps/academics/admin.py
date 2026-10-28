from django.contrib import admin

from .models import Department, Section, Semester, Subject


class DepartmentAdmin(admin.ModelAdmin):
    """Admin for Department."""

    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    ordering = ['code']


class SemesterAdmin(admin.ModelAdmin):
    """Admin for Semester."""

    list_display = ['department', 'number']
    list_filter = ['department']
    ordering = ['department__code', 'number']


class SectionAdmin(admin.ModelAdmin):
    """Admin for Section."""

    list_display = ['semester', 'name', 'shift']
    list_filter = ['semester__department', 'shift']
    search_fields = ['semester__department__code', 'name']
    ordering = ['semester', 'name']


class SubjectAdmin(admin.ModelAdmin):
    """Admin for Subject."""

    list_display = ['code', 'name', 'semester', 'subject_type']
    list_filter = ['semester__department', 'subject_type']
    search_fields = ['code', 'name']
    ordering = ['code']


admin.site.register(Department, DepartmentAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Subject, SubjectAdmin)
