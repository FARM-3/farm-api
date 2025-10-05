# users/backends.py
from django.contrib.auth.backends import BaseBackend
from .models import User


class PhonePinBackend(BaseBackend):
    """
    Custom authentication backend that allows users to login with:
    - Phone number (instead of username)
    - 4-digit PIN (instead of password)
    
    This backend is used by Django's authenticate() function.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user based on phone number and PIN.
        
        Args:
            request: The HTTP request object
            username (str): Phone number (we call it username for Django compatibility)
            password (str): 4-digit PIN
            **kwargs: Additional keyword arguments
        
        Returns:
            User: Authenticated user if credentials are valid
            None: If authentication fails
        """
        if username is None or password is None:
            return None
        
        try:
            # Try to get user by phone number
            user = User.objects.get(phone=username)
        except User.DoesNotExist:
            # User not found - return None (invalid credentials)
            return None
        
        # Check if the PIN matches
        # check_password() compares the raw PIN with the hashed version in DB
        if user.check_password(password):
            # PIN is correct - return the user
            return user
        
        # PIN is incorrect - return None
        return None
    
    def get_user(self, user_id):
        """
        Get a user by their ID.
        This is used by Django to retrieve the user after they've been authenticated.
        
        Args:
            user_id (int): The user's primary key
        
        Returns:
            User: User instance if found
            None: If user doesn't exist
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None