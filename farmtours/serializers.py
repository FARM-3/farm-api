# farmtours/serializers.py
from rest_framework import serializers
from .models import TourPackage, TourAvailability, TourBooking
from datetime import date


# ============================================
# TOUR PACKAGE SERIALIZER
# ============================================
class TourPackageSerializer(serializers.ModelSerializer):
    """
    Serializer for TourPackage model.
    Shows available tour packages to customers.
    """

    duration_display = serializers.CharField(source='get_duration_display', read_only=True)

    class Meta:
        model = TourPackage
        fields = [
            'id',
            'name',
            'description',
            'duration',
            'duration_display',
            'price_per_person',
            'max_group_size',
            'min_group_size',
            'includes',
            'is_active'
        ]
        read_only_fields = ['id']


# ============================================
# TOUR AVAILABILITY SERIALIZER
# ============================================
class TourAvailabilitySerializer(serializers.ModelSerializer):
    """
    Serializer for TourAvailability model.
    Shows available time slots for bookings.
    """

    time_slot_display = serializers.CharField(source='get_time_slot_display', read_only=True)
    tour_package_name = serializers.CharField(source='tour_package.name', read_only=True)

    class Meta:
        model = TourAvailability
        fields = [
            'id',
            'tour_package',
            'tour_package_name',
            'date',
            'time_slot',
            'time_slot_display',
            'available_spots',
            'is_available'
        ]
        read_only_fields = ['id']


# ============================================
# TOUR BOOKING SERIALIZER (for creating bookings)
# ============================================
class CreateTourBookingSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new tour bookings.
    """

    class Meta:
        model = TourBooking
        fields = [
            'tour_package',
            'availability',
            'customer_name',
            'customer_email',
            'customer_phone',
            'number_of_people',
            'special_requests'
        ]

    def validate(self, data):
        """
        Validate booking data.
        """
        tour_package = data['tour_package']
        availability = data['availability']
        number_of_people = data['number_of_people']

        # Check if availability belongs to the selected tour package
        if availability.tour_package != tour_package:
            raise serializers.ValidationError({
                "availability": "Selected time slot does not belong to this tour package"
            })

        # Check if tour date is in the future
        if availability.date < date.today():
            raise serializers.ValidationError({
                "availability": "Cannot book tours for past dates"
            })

        # Check if enough spots are available
        if not availability.has_available_spots(number_of_people):
            raise serializers.ValidationError({
                "number_of_people": f"Not enough spots available. Only {availability.available_spots} spots left."
            })

        # Check group size limits
        if number_of_people < tour_package.min_group_size:
            raise serializers.ValidationError({
                "number_of_people": f"Minimum group size is {tour_package.min_group_size} people"
            })

        if number_of_people > tour_package.max_group_size:
            raise serializers.ValidationError({
                "number_of_people": f"Maximum group size is {tour_package.max_group_size} people"
            })

        return data

    def create(self, validated_data):
        """
        Create booking and reduce available spots.
        """
        booking = TourBooking.objects.create(**validated_data)

        # Reduce available spots
        availability = validated_data['availability']
        availability.available_spots -= validated_data['number_of_people']
        if availability.available_spots == 0:
            availability.is_available = False
        availability.save()

        return booking


# ============================================
# TOUR BOOKING SERIALIZER (for viewing bookings)
# ============================================
class TourBookingSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing tour booking details.
    """

    tour_package_name = serializers.CharField(source='tour_package.name', read_only=True)
    tour_duration = serializers.CharField(source='tour_package.get_duration_display', read_only=True)
    tour_date = serializers.DateField(source='availability.date', read_only=True)
    tour_time = serializers.CharField(source='availability.get_time_slot_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TourBooking
        fields = [
            'id',
            'booking_reference',
            'tour_package',
            'tour_package_name',
            'tour_duration',
            'tour_date',
            'tour_time',
            'customer_name',
            'customer_email',
            'customer_phone',
            'number_of_people',
            'special_requests',
            'total_price',
            'status',
            'status_display',
            'is_paid',
            'payment_method',
            'created_at',
            'confirmed_at'
        ]
        read_only_fields = [
            'id',
            'booking_reference',
            'total_price',
            'created_at',
            'confirmed_at'
        ]


# ============================================
# CHECK AVAILABILITY SERIALIZER
# ============================================
class CheckAvailabilitySerializer(serializers.Serializer):
    """
    Serializer for checking tour availability.
    """

    tour_package_id = serializers.IntegerField(required=True)
    date = serializers.DateField(required=True)

    def validate_date(self, value):
        """Ensure date is not in the past."""
        if value < date.today():
            raise serializers.ValidationError("Cannot check availability for past dates")
        return value
