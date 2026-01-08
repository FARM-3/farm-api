"""
Middleware to track the current authenticated user in thread-local storage.
This makes the user available to Django signals for activity logging.

This is a standard Django pattern used by libraries like django-crum.
Thread-local storage ensures each request is isolated with no side effects.
"""
import threading
from django.utils.deprecation import MiddlewareMixin

# Thread-local storage to hold the current user
_thread_locals = threading.local()


def get_current_user():
    """
    Get the currently authenticated user from thread-local storage.
    Returns None if no user is set or if user is not authenticated.
    """
    return getattr(_thread_locals, 'user', None)


def set_current_user(user):
    """
    Set the current user in thread-local storage.
    """
    _thread_locals.user = user


def clear_current_user():
    """
    Clear the current user from thread-local storage.
    """
    if hasattr(_thread_locals, 'user'):
        del _thread_locals.user


class CurrentUserMiddleware(MiddlewareMixin):
    """
    Middleware that stores the current authenticated user in thread-local storage.

    This allows signals and other code to access the user without needing
    the request object. Each request is isolated in its own thread.
    """

    def process_request(self, request):
        """
        Store the authenticated user when request starts.
        """
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            set_current_user(user)
        else:
            set_current_user(None)

    def process_response(self, request, response):
        """
        Clear the user from thread-local storage when request completes.
        """
        clear_current_user()
        return response

    def process_exception(self, request, exception):
        """
        Clear the user even if an exception occurs.
        """
        clear_current_user()
        return None
