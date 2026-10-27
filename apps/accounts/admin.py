from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom email-based User model."""

    # Show the most useful account fields in the change list.
    list_display = ('email', 'full_name', 'role', 'is_active', 'is_staff')
    # Allow filtering the change list by role and account flags.
    list_filter = ('role', 'is_active', 'is_staff')
    # Enable searching by email and name.
    search_fields = ('email', 'full_name')
    # Keep the change list ordered consistently by email.
    ordering = ('email',)

    # Lay out the edit form for existing users.
    fieldsets = (
        # Credentials section containing the login email and password.
        (None, {'fields': ('email', 'password')}),
        # Personal information section containing the display name.
        ('Personal info', {'fields': ('full_name',)}),
        # Permissions section containing the role and account flags.
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        # Audit section containing login and creation timestamps.
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Lay out the creation form for new users.
    add_fieldsets = (
        # Wide form section with the required account fields.
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2'),
        }),
    )
