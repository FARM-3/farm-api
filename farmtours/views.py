# farmtours/views.py
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from datetime import date, timedelta
from .models import TourPackage, TourAvailability, TourBooking
from .serializers import (
    TourPackageSerializer,
    TourAvailabilitySerializer,
    CreateTourBookingSerializer,
    TourBookingSerializer,
    CheckAvailabilitySerializer
)
from .utils import send_booking_confirmation_email, send_booking_confirmed_email


# ============================================
# LIST ALL TOUR PACKAGES
# ============================================
@extend_schema(
    responses={200: TourPackageSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def list_tour_packages_view(request):
    """
    Get all active tour packages.

    Endpoint: GET /api/farmtours/packages/

    Response:
        [
            {
                "id": 1,
                "name": "Coffee Farm Tour",
                "description": "Experience the journey from bean to cup...",
                "duration": "2_hours",
                "duration_display": "2 Hours",
                "price_per_person": "25000.00",
                "max_group_size": 20,
                "min_group_size": 1,
                "includes": "Coffee tasting, guided tour, refreshments",
                "is_active": true
            }
        ]
    """
    packages = TourPackage.objects.filter(is_active=True)
    serializer = TourPackageSerializer(packages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================
# GET SINGLE TOUR PACKAGE
# ============================================
@extend_schema(
    responses={200: TourPackageSerializer}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_tour_package_view(request, package_id):
    """
    Get details of a specific tour package.

    Endpoint: GET /api/farmtours/packages/<package_id>/
    """
    try:
        package = TourPackage.objects.get(id=package_id, is_active=True)
    except TourPackage.DoesNotExist:
        return Response(
            {"error": "Tour package not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = TourPackageSerializer(package)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================
# CHECK AVAILABILITY FOR A TOUR
# ============================================
@extend_schema(
    request=CheckAvailabilitySerializer,
    responses={200: TourAvailabilitySerializer(many=True)}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def check_availability_view(request):
    """
    Check available time slots for a specific tour package and date.

    Endpoint: POST /api/farmtours/check-availability/

    Request body:
        {
            "tour_package_id": 1,
            "date": "2024-02-01"
        }

    Response:
        [
            {
                "id": 1,
                "tour_package": 1,
                "tour_package_name": "Coffee Farm Tour",
                "date": "2024-02-01",
                "time_slot": "09:00",
                "time_slot_display": "9:00 AM",
                "available_spots": 15,
                "is_available": true
            }
        ]
    """
    serializer = CheckAvailabilitySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    tour_package_id = serializer.validated_data['tour_package_id']
    check_date = serializer.validated_data['date']

    # Get available slots
    availabilities = TourAvailability.objects.filter(
        tour_package_id=tour_package_id,
        date=check_date,
        is_available=True,
        available_spots__gt=0
    )

    if not availabilities.exists():
        return Response(
            {"message": "No available slots for this date"},
            status=status.HTTP_200_OK
        )

    availability_serializer = TourAvailabilitySerializer(availabilities, many=True)
    return Response(availability_serializer.data, status=status.HTTP_200_OK)


# ============================================
# CREATE TOUR BOOKING
# ============================================
@extend_schema(
    request=CreateTourBookingSerializer,
    responses={201: TourBookingSerializer}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_booking_view(request):
    """
    Create a new tour booking.

    Endpoint: POST /api/farmtours/bookings/

    Request body:
        {
            "tour_package": 1,
            "availability": 1,
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "customer_phone": "+256700000000",
            "number_of_people": 2,
            "special_requests": "Vegetarian meals please"
        }

    Response (success):
        {
            "id": 1,
            "booking_reference": "RFT20240115001",
            "tour_package": 1,
            "tour_package_name": "Coffee Farm Tour",
            "tour_duration": "2 Hours",
            "tour_date": "2024-02-01",
            "tour_time": "9:00 AM",
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "customer_phone": "+256700000000",
            "number_of_people": 2,
            "special_requests": "Vegetarian meals please",
            "total_price": "50000.00",
            "status": "pending",
            "status_display": "Pending Confirmation",
            "is_paid": false,
            "created_at": "2024-01-15T10:30:00Z"
        }
    """
    serializer = CreateTourBookingSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create booking
    booking = serializer.save()

    # Send confirmation email
    send_booking_confirmation_email(booking)

    # Return booking details
    booking_serializer = TourBookingSerializer(booking)
    return Response(
        booking_serializer.data,
        status=status.HTTP_201_CREATED
    )


# ============================================
# GET BOOKING BY REFERENCE
# ============================================
@extend_schema(
    responses={200: TourBookingSerializer}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_booking_view(request, booking_reference):
    """
    Get booking details by booking reference.

    Endpoint: GET /api/farmtours/bookings/<booking_reference>/
    """
    try:
        booking = TourBooking.objects.get(booking_reference=booking_reference)
    except TourBooking.DoesNotExist:
        return Response(
            {"error": "Booking not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = TourBookingSerializer(booking)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================
# CANCEL BOOKING
# ============================================
@extend_schema(
    responses={200: OpenApiResponse(description="Booking cancelled")}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def cancel_booking_view(request, booking_reference):
    """
    Cancel a tour booking.

    Endpoint: POST /api/farmtours/bookings/<booking_reference>/cancel/

    Response:
        {
            "message": "Booking cancelled successfully",
            "booking_reference": "RFT20240115001"
        }
    """
    try:
        booking = TourBooking.objects.get(booking_reference=booking_reference)
    except TourBooking.DoesNotExist:
        return Response(
            {"error": "Booking not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if booking can be cancelled
    if booking.status in ['cancelled', 'completed']:
        return Response(
            {"error": f"Cannot cancel a {booking.status} booking"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if tour date has passed
    if booking.availability.date < date.today():
        return Response(
            {"error": "Cannot cancel bookings for past dates"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Cancel booking
    booking.cancel_booking()

    return Response({
        "message": "Booking cancelled successfully",
        "booking_reference": booking.booking_reference
    }, status=status.HTTP_200_OK)


# ============================================
# ADMIN: LIST ALL BOOKINGS
# ============================================
@extend_schema(
    responses={200: TourBookingSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Only authenticated admins can view all bookings
def list_all_bookings_view(request):
    """
    Get all bookings (Admin only).

    Endpoint: GET /api/farmtours/admin/bookings/

    Headers:
        Authorization: Bearer <admin_access_token>
    """
    bookings = TourBooking.objects.all()

    # Filter by status if provided
    status_filter = request.query_params.get('status', None)
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    # Filter by date range
    date_from = request.query_params.get('date_from', None)
    date_to = request.query_params.get('date_to', None)

    if date_from:
        bookings = bookings.filter(availability__date__gte=date_from)
    if date_to:
        bookings = bookings.filter(availability__date__lte=date_to)

    serializer = TourBookingSerializer(bookings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================
# ADMIN: CONFIRM BOOKING
# ============================================
@extend_schema(
    responses={200: TourBookingSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Only authenticated admins
def confirm_booking_view(request, booking_id):
    """
    Confirm a pending booking (Admin only).

    Endpoint: POST /api/farmtours/admin/bookings/<booking_id>/confirm/

    Headers:
        Authorization: Bearer <admin_access_token>
    """
    try:
        booking = TourBooking.objects.get(id=booking_id)
    except TourBooking.DoesNotExist:
        return Response(
            {"error": "Booking not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if booking.status != 'pending':
        return Response(
            {"error": f"Cannot confirm a {booking.status} booking"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Confirm booking
    booking.confirm_booking()

    # Send confirmation email to customer
    send_booking_confirmed_email(booking)

    serializer = TourBookingSerializer(booking)
    return Response(serializer.data, status=status.HTTP_200_OK)
