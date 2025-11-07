
# users/urls.py
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .views import logout_view

"""
URL patterns for the users app.
All these URLs will be prefixed with /api/users/ in the main project urls.py

Available endpoints:
- POST /api/users/login/                          → Login with phone + PIN
- POST /api/users/logout/                         → Logout and invalidate session/token
- POST /api/users/security-question/              → Get security question
- POST /api/users/reset-pin/                      → Reset PIN with security answer
- POST /api/users/token/refresh/                  → Refresh JWT access token
- GET  /api/users/me/                             → Get current user info (requires auth)
- POST /api/users/random-security-questions/      → Get 3 random security questions (first login)
- POST /api/users/setup-security-answers/         → Setup security answers (first login)
- POST /api/users/verify-answers-reset-pin/       → Verify answers and reset PIN

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

    # ---- Logout Endpoint ----
    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

    # ---- Security Questions Setup (First Login) ----
    path(
        'random-security-questions/',
        views.get_random_security_questions_view,
        name='random-security-questions'
    ),

    path(
        'setup-security-answers/',
        views.setup_security_answers_view,
        name='setup-security-answers'
    ),

    # ---- Security Questions for PIN Reset ----
    path(
        'verify-answers-reset-pin/',
        views.verify_security_answers_and_reset_pin_view,
        name='verify-answers-reset-pin'
    ),
]