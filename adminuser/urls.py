# adminuser/urls.py
from django.urls import path
from . import views

app_name = 'adminuser'

urlpatterns = [
    # Admin authentication endpoints
    path('login/', views.admin_login_view, name='admin-login'),
    path('me/', views.admin_me_view, name='admin-me'),
    path('logout/', views.admin_logout_view, name='admin-logout'),

    # Password reset endpoints
    path('request-password-reset/', views.request_password_reset_view, name='request-password-reset'),
    path('verify-otp/', views.verify_otp_view, name='verify-otp'),
    path('reset-password/', views.reset_password_view, name='reset-password'),
]
