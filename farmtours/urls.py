# farmtours/urls.py
from django.urls import path
from . import views

app_name = 'farmtours'

urlpatterns = [
    # Public endpoints - Tour packages
    path('packages/', views.list_tour_packages_view, name='list-packages'),
    path('packages/<int:package_id>/', views.get_tour_package_view, name='get-package'),

    # Public endpoints - Availability
    path('check-availability/', views.check_availability_view, name='check-availability'),

    # Public endpoints - Bookings
    path('bookings/', views.create_booking_view, name='create-booking'),
    path('bookings/<str:booking_reference>/', views.get_booking_view, name='get-booking'),
    path('bookings/<str:booking_reference>/cancel/', views.cancel_booking_view, name='cancel-booking'),

    # Admin endpoints - Booking management
    path('admin/bookings/', views.list_all_bookings_view, name='list-all-bookings'),
    path('admin/bookings/<int:booking_id>/confirm/', views.confirm_booking_view, name='confirm-booking'),
]
