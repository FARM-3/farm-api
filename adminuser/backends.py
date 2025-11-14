# adminuser/backends.py
from django.contrib.auth.backends import BaseBackend
from .models import AdminUser


class EmailPasswordBackend(BaseBackend):
    """
    Custom authentication backend that allows admin users to login with:
    - Email address (instead of username)
    - Password (standard password authentication)

    This backend is used by Django's authenticate() function for admin users.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate an admin user based on email and password.

        Args:
            request: The HTTP request object
            username (str): Email address (we call it username for Django compatibility)
            password (str): Admin user's password
            **kwargs: Additional keyword arguments

        Returns:
            AdminUser: Authenticated admin user if credentials are valid
            None: If authentication fails
        """
        if username is None or password is None:
            return None

        try:
            # Try to get admin user by email (case-insensitive)
            user = AdminUser.objects.get(email__iexact=username)
        except AdminUser.DoesNotExist:
            # Admin user not found - return None (invalid credentials)
            return None

        # Check if the password matches
        # check_password() compares the raw password with the hashed version in DB
        if user.check_password(password):
            # Password is correct - return the admin user
            return user

        # Password is incorrect - return None
        return None

    def get_user(self, user_id):
        """
        Get an admin user by their ID.
        This is used by Django to retrieve the user after they've been authenticated.

        Args:
            user_id (int): The admin user's primary key

        Returns:
            AdminUser: Admin user instance if found
            None: If admin user doesn't exist
        """
        try:
            return AdminUser.objects.get(pk=user_id)
        except AdminUser.DoesNotExist:
            return None
