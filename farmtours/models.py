from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


# ============================================
# TOUR PACKAGE MODEL
# ============================================
class TourPackage(models.Model):
    """
    Different tour packages available at Rugyeyo Farm.
    Example: Basic Tour, Premium Experience, Educational Tour, etc.
    """

    DURATION_CHOICES = [
        ('1_hour', '1 Hour'),
        ('2_hours', '2 Hours'),
        ('half_day', 'Half Day (4 hours)'),
        ('full_day', 'Full Day (8 hours)'),
    ]

    name = models.CharField(
        max_length=200,
        help_text="Tour package name (e.g., 'Coffee Farm Tour', 'Premium Experience')"
    )

    description = models.TextField(
        help_text="Detailed description of what's included in the tour"
    )

    duration = models.CharField(
        max_length=20,
        choices=DURATION_CHOICES,
        default='2_hours',
        help_text="Duration of the tour"
    )

    price_per_person = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per person in your currency"
    )

    max_group_size = models.PositiveIntegerField(
        default=20,
        help_text="Maximum number of people allowed per tour"
    )

    min_group_size = models.PositiveIntegerField(
        default=1,
        help_text="Minimum number of people required for the tour"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Is this tour package currently available for booking?"
    )

    includes = models.TextField(
        blank=True,
        help_text="What's included (refreshments, guide, transport, etc.)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tour Package"
        verbose_name_plural = "Tour Packages"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.get_duration_display()}"


# ============================================
# TOUR AVAILABILITY MODEL
# ============================================
class TourAvailability(models.Model):
    """
    Defines available time slots for tours on specific dates.
    """

    TIME_SLOT_CHOICES = [
        ('09:00', '9:00 AM'),
        ('10:00', '10:00 AM'),
        ('11:00', '11:00 AM'),
        ('12:00', '12:00 PM'),
        ('13:00', '1:00 PM'),
        ('14:00', '2:00 PM'),
        ('15:00', '3:00 PM'),
        ('16:00', '4:00 PM'),
    ]

    tour_package = models.ForeignKey(
        TourPackage,
        on_delete=models.CASCADE,
        related_name='availabilities',
        help_text="Which tour package this availability is for"
    )

    date = models.DateField(
        help_text="Date when this tour is available"
    )

    time_slot = models.CharField(
        max_length=5,
        choices=TIME_SLOT_CHOICES,
        help_text="Time slot for the tour"
    )

    available_spots = models.PositiveIntegerField(
        help_text="Number of spots available for this time slot"
    )

    is_available = models.BooleanField(
        default=True,
        help_text="Is this time slot still available for booking?"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tour Availability"
        verbose_name_plural = "Tour Availabilities"
        ordering = ['date', 'time_slot']
        unique_together = ('tour_package', 'date', 'time_slot')

    def __str__(self):
        return f"{self.tour_package.name} - {self.date} at {self.get_time_slot_display()}"

    def has_available_spots(self, number_of_people):
        """Check if there are enough spots available."""
        return self.is_available and self.available_spots >= number_of_people


# ============================================
# TOUR BOOKING MODEL
# ============================================
class TourBooking(models.Model):
    """
    Customer bookings for farm tours.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]

    # Booking Reference (auto-generated)
    booking_reference = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Unique booking reference number"
    )

    # Tour Details
    tour_package = models.ForeignKey(
        TourPackage,
        on_delete=models.PROTECT,
        related_name='bookings',
        help_text="Selected tour package"
    )

    availability = models.ForeignKey(
        TourAvailability,
        on_delete=models.PROTECT,
        related_name='bookings',
        help_text="Selected date and time slot"
    )

    # Customer Information
    customer_name = models.CharField(
        max_length=200,
        help_text="Full name of the person booking"
    )

    customer_email = models.EmailField(
        help_text="Email address for confirmation"
    )

    customer_phone = models.CharField(
        max_length=20,
        help_text="Phone number"
    )

    number_of_people = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        help_text="Number of people in the group"
    )

    # Additional Details
    special_requests = models.TextField(
        blank=True,
        help_text="Any special requests or dietary requirements"
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total cost for the booking"
    )

    # Booking Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the booking"
    )

    # Admin Notes
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes (not visible to customer)"
    )

    # Payment Info (optional)
    is_paid = models.BooleanField(
        default=False,
        help_text="Has the customer paid?"
    )

    payment_method = models.CharField(
        max_length=50,
        blank=True,
        help_text="Payment method used"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Tour Booking"
        verbose_name_plural = "Tour Bookings"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.booking_reference} - {self.customer_name} ({self.status})"

    def save(self, *args, **kwargs):
        """Auto-generate booking reference and calculate total price."""
        if not self.booking_reference:
            # Generate unique booking reference (e.g., RFT20240115001)
            import random
            import string
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.digits, k=3))
            self.booking_reference = f"RFT{date_str}{random_str}"

        # Calculate total price if not set
        if not self.total_price:
            self.total_price = self.tour_package.price_per_person * self.number_of_people

        super().save(*args, **kwargs)

    def confirm_booking(self):
        """Mark booking as confirmed."""
        self.status = 'confirmed'
        self.confirmed_at = timezone.now()
        self.save()

    def cancel_booking(self):
        """Cancel the booking and restore availability."""
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()

        # Restore available spots
        self.availability.available_spots += self.number_of_people
        self.availability.save()

        self.save()
