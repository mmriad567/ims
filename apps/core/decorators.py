from functools import wraps
from django.http import HttpResponseForbidden


def role_required(role):
    """Restrict a view to a specific user role; returns 403 otherwise."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated or request.user.role != role:
                return HttpResponseForbidden("You don't have access to this page")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
