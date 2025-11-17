from django.contrib import admin
from .models import TourPackage, TourAvailability, TourBooking


# ============================================
# TOUR PACKAGE ADMIN
# ============================================
@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    """
    Admin configuration for TourPackage model.
    """
    list_display = ['name', 'duration', 'price_per_person', 'max_group_size', 'is_active', 'created_at']
    list_filter = ['is_active', 'duration', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'duration', 'is_active')
        }),
        ('Pricing & Capacity', {
            'fields': ('price_per_person', 'min_group_size', 'max_group_size')
        }),
        ('Includes', {
            'fields': ('includes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


# ============================================
# TOUR AVAILABILITY ADMIN
# ============================================
@admin.register(TourAvailability)
class TourAvailabilityAdmin(admin.ModelAdmin):
    """
    Admin configuration for TourAvailability model.
    """
    list_display = ['tour_package', 'date', 'time_slot', 'available_spots', 'is_available', 'created_at']
    list_filter = ['is_available', 'date', 'time_slot', 'tour_package']
    search_fields = ['tour_package__name']
    ordering = ['-date', 'time_slot']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Tour Details', {
            'fields': ('tour_package', 'date', 'time_slot')
        }),
        ('Availability', {
            'fields': ('available_spots', 'is_available')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


# ============================================
# TOUR BOOKING ADMIN
# ============================================
@admin.register(TourBooking)
class TourBookingAdmin(admin.ModelAdmin):
    """
    Admin configuration for TourBooking model.
    """
    list_display = [
        'booking_reference',
        'customer_name',
        'customer_email',
        'tour_package',
        'get_tour_date',
        'number_of_people',
        'total_price',
        'status',
        'is_paid',
        'created_at'
    ]
    list_filter = ['status', 'is_paid', 'created_at', 'tour_package']
    search_fields = [
        'booking_reference',
        'customer_name',
        'customer_email',
        'customer_phone'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'booking_reference',
        'total_price',
        'created_at',
        'updated_at',
        'confirmed_at',
        'cancelled_at'
    ]

    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_reference', 'status', 'created_at')
        }),
        ('Tour Details', {
            'fields': ('tour_package', 'availability', 'number_of_people', 'total_price')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Special Requests', {
            'fields': ('special_requests',)
        }),
        ('Payment', {
            'fields': ('is_paid', 'payment_method')
        }),
        ('Admin Notes', {
            'fields': ('admin_notes',)
        }),
        ('Timestamps', {
            'fields': ('updated_at', 'confirmed_at', 'cancelled_at')
        }),
    )

    def get_tour_date(self, obj):
        """Display tour date in list view."""
        return obj.availability.date
    get_tour_date.short_description = 'Tour Date'
    get_tour_date.admin_order_field = 'availability__date'

    actions = ['confirm_bookings', 'cancel_bookings']

    def confirm_bookings(self, request, queryset):
        """Bulk confirm selected bookings."""
        count = 0
        for booking in queryset.filter(status='pending'):
            booking.confirm_booking()
            count += 1
        self.message_user(request, f'{count} booking(s) confirmed successfully.')
    confirm_bookings.short_description = "Confirm selected bookings"

    def cancel_bookings(self, request, queryset):
        """Bulk cancel selected bookings."""
        count = 0
        for booking in queryset.exclude(status__in=['cancelled', 'completed']):
            booking.cancel_booking()
            count += 1
        self.message_user(request, f'{count} booking(s) cancelled successfully.')
    cancel_bookings.short_description = "Cancel selected bookings"
