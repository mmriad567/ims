from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import StudentProfile, TeacherProfile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom email-based User model."""

    list_display = ('email', 'full_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'full_name')
    autocomplete_fields = []
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """Admin for StudentProfile."""

    list_display = ['roll_no', 'user', 'section', 'session', 'is_active']
    list_filter = ['is_active', 'section__semester__department', 'section__shift']
    search_fields = ['roll_no', 'registration_no', 'user__email', 'user__full_name']
    autocomplete_fields = ['user', 'section']


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    """Admin for TeacherProfile."""

    list_display = ['user', 'department', 'designation']
    list_filter = ['designation', 'department']
    search_fields = ['user__email', 'user__full_name']
    autocomplete_fields = ['user', 'department']
