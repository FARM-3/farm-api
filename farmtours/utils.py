# farmtours/utils.py
from django.core.mail import send_mail
from django.conf import settings


def send_booking_confirmation_email(booking):
    """
    Send booking confirmation email to customer.

    Args:
        booking: TourBooking instance

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = f"Booking Confirmation - Rugyeyo Farm Tour ({booking.booking_reference})"

    message = f"""
Dear {booking.customer_name},

Thank you for booking a farm tour with Rugyeyo Farm!

Your booking has been received and is pending confirmation.

BOOKING DETAILS:
----------------
Booking Reference: {booking.booking_reference}
Tour Package: {booking.tour_package.name}
Date: {booking.availability.date.strftime('%A, %B %d, %Y')}
Time: {booking.availability.get_time_slot_display()}
Duration: {booking.tour_package.get_duration_display()}
Number of People: {booking.number_of_people}
Total Price: {booking.total_price}

{f'Special Requests: {booking.special_requests}' if booking.special_requests else ''}

NEXT STEPS:
-----------
1. You will receive a confirmation email once your booking is approved
2. Please arrive 15 minutes before your scheduled tour time
3. Bring comfortable walking shoes and weather-appropriate clothing

LOCATION:
---------
Rugyeyo Farm
[Add your farm address here]

CONTACT:
--------
If you have any questions, please contact us:
Email: {settings.DEFAULT_FROM_EMAIL}
Phone: [Add your phone number]

We look forward to welcoming you to Rugyeyo Farm!

Best regards,
Rugyeyo Farm Team
    """

    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .header {{
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background-color: white;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .booking-details {{
            background-color: #f0f0f0;
            padding: 20px;
            border-left: 4px solid #4CAF50;
            margin: 20px 0;
        }}
        .booking-ref {{
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
            text-align: center;
            padding: 15px;
            background-color: #e8f5e9;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            font-size: 12px;
            color: #666;
        }}
        .highlight {{
            color: #4CAF50;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Booking Confirmation</h1>
            <p>Rugyeyo Farm Tour</p>
        </div>
        <div class="content">
            <p>Dear <strong>{booking.customer_name}</strong>,</p>

            <p>Thank you for booking a farm tour with Rugyeyo Farm!</p>

            <p>Your booking has been received and is <span class="highlight">pending confirmation</span>.</p>

            <div class="booking-ref">
                Booking Reference: {booking.booking_reference}
            </div>

            <div class="booking-details">
                <h3>BOOKING DETAILS:</h3>
                <p><strong>Tour Package:</strong> {booking.tour_package.name}</p>
                <p><strong>Date:</strong> {booking.availability.date.strftime('%A, %B %d, %Y')}</p>
                <p><strong>Time:</strong> {booking.availability.get_time_slot_display()}</p>
                <p><strong>Duration:</strong> {booking.tour_package.get_duration_display()}</p>
                <p><strong>Number of People:</strong> {booking.number_of_people}</p>
                <p><strong>Total Price:</strong> {booking.total_price}</p>
                {f'<p><strong>Special Requests:</strong> {booking.special_requests}</p>' if booking.special_requests else ''}
            </div>

            <h3>NEXT STEPS:</h3>
            <ul>
                <li>You will receive a confirmation email once your booking is approved</li>
                <li>Please arrive 15 minutes before your scheduled tour time</li>
                <li>Bring comfortable walking shoes and weather-appropriate clothing</li>
            </ul>

            <h3>LOCATION:</h3>
            <p>
                Rugyeyo Farm<br>
                [Add your farm address here]
            </p>

            <h3>CONTACT:</h3>
            <p>
                If you have any questions, please contact us:<br>
                Email: {settings.DEFAULT_FROM_EMAIL}<br>
                Phone: [Add your phone number]
            </p>

            <p>We look forward to welcoming you to Rugyeyo Farm!</p>

            <div class="footer">
                <p>Best regards,<br>Rugyeyo Farm Team</p>
            </div>
        </div>
    </div>
</body>
</html>
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.customer_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending booking confirmation email: {str(e)}")
        return False


def send_booking_confirmed_email(booking):
    """
    Send email when booking is confirmed by admin.
    """
    subject = f"Your Tour Booking is Confirmed! - {booking.booking_reference}"

    message = f"""
Dear {booking.customer_name},

Great news! Your farm tour booking has been CONFIRMED!

Booking Reference: {booking.booking_reference}
Tour Date: {booking.availability.date.strftime('%A, %B %d, %Y')}
Time: {booking.availability.get_time_slot_display()}

Please save this email for your records.

We look forward to seeing you!

Best regards,
Rugyeyo Farm Team
    """

    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4CAF50; color: white; padding: 30px; text-align: center; }}
        .content {{ background-color: white; padding: 30px; }}
        .confirmed {{ font-size: 28px; color: #4CAF50; text-align: center; padding: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✓ Booking Confirmed!</h1>
        </div>
        <div class="content">
            <p>Dear <strong>{booking.customer_name}</strong>,</p>
            <div class="confirmed">
                Your tour booking is CONFIRMED!
            </div>
            <p><strong>Booking Reference:</strong> {booking.booking_reference}</p>
            <p><strong>Date:</strong> {booking.availability.date.strftime('%A, %B %d, %Y')}</p>
            <p><strong>Time:</strong> {booking.availability.get_time_slot_display()}</p>
            <p>We look forward to seeing you!</p>
        </div>
    </div>
</body>
</html>
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.customer_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending confirmation email: {str(e)}")
        return False
