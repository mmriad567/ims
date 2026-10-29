from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse


@login_required
def dashboard(request):
    """Route user to role-specific dashboard template."""
    role = request.user.role
    templates = {
        'admin': 'dashboards/admin.html',
        'teacher': 'dashboards/teacher.html',
        'student': 'dashboards/student.html',
    }
    template = templates.get(role)
    if not template:
        return HttpResponse('Invalid role on user account', status=403)
    return render(request, template)
