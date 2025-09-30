
# users/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

"""
URL patterns for the users app.
All these URLs will be prefixed with /api/users/ in the main project urls.py

Available endpoints:
- POST /api/users/login/              → Login with phone + PIN
- POST /api/users/security-question/  → Get security question
- POST /api/users/reset-pin/          → Reset PIN with security answer
- POST /api/users/token/refresh/      → Refresh JWT access token
- GET  /api/users/me/                 → Get current user info (requires auth)
"""

app_name = 'users'  # Namespace for reverse URL lookups

urlpatterns = [
    # ---- Authentication Endpoints ----
    path(
        'login/', 
        views.login_view, 
        name='login'
    ),
    
    # ---- PIN Reset Endpoints ----
    path(
        'security-question/', 
        views.get_security_question_view, 
        name='security-question'
    ),
    
    path(
        'reset-pin/', 
        views.reset_pin_view, 
        name='reset-pin'
    ),
    
    # ---- JWT Token Management ----
    path(
        'token/refresh/', 
        TokenRefreshView.as_view(), 
        name='token-refresh'
    ),
    # This endpoint allows frontend to get a new access token
    # when the current one expires, using the refresh token.
    # Request: POST with {"refresh": "your_refresh_token"}
    # Response: {"access": "new_access_token"}
    
    # ---- User Info Endpoint ----
    path(
        'me/', 
        views.me_view, 
        name='me'
    ),
]