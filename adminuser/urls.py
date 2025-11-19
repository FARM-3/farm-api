# adminuser/urls.py
from django.urls import path
from . import views

app_name = 'adminuser'

urlpatterns = [
    # Admin signup and authentication endpoints
    path('signup/', views.admin_signup_view, name='admin-signup'),
    path('login/', views.admin_login_view, name='admin-login'),
    path('me/', views.admin_me_view, name='admin-me'),
    path('logout/', views.admin_logout_view, name='admin-logout'),

    # Email verification endpoints
    path('send-verification-email/', views.send_verification_email_view, name='send-verification-email'),
    path('check-verification/<str:email>/', views.check_verification_view, name='check-verification'),
    path('verify-email/', views.verify_email_view, name='verify-email'),

    # Password reset endpoints
    path('request-password-reset/', views.request_password_reset_view, name='request-password-reset'),
    path('verify-otp/', views.verify_otp_view, name='verify-otp'),
    path('reset-password/', views.reset_password_view, name='reset-password'),
]
