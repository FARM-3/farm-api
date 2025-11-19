# adminuser/utils.py
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailVerification


def send_otp_email(email, otp_code, admin_name="Admin"):
    """
    Send OTP code to admin user's email for password reset.

    Args:
        email (str): Admin user's email address
        otp_code (str): 6-digit OTP code
        admin_name (str): Admin user's name

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = "Password Reset OTP - Farm Management System"

    message = f"""
Hello {admin_name},

You have requested to reset your password for the Farm Management System Admin Portal.

Your One-Time Password (OTP) is: {otp_code}

This OTP is valid for 10 minutes only.

If you did not request this password reset, please ignore this email or contact support immediately.

Best regards,
Farm Management System Team
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
            border-radius: 10px;
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
        .otp-box {{
            background-color: #f0f0f0;
            border: 2px dashed #4CAF50;
            padding: 20px;
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            color: #4CAF50;
            margin: 20px 0;
            letter-spacing: 5px;
        }}
        .warning {{
            color: #d32f2f;
            font-size: 14px;
            margin-top: 20px;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Password Reset Request</h2>
        </div>
        <div class="content">
            <p>Hello <strong>{admin_name}</strong>,</p>

            <p>You have requested to reset your password for the <strong>Farm Management System Admin Portal</strong>.</p>

            <p>Your One-Time Password (OTP) is:</p>

            <div class="otp-box">
                {otp_code}
            </div>

            <p><strong>This OTP is valid for 10 minutes only.</strong></p>

            <p class="warning">
                ⚠️ If you did not request this password reset, please ignore this email or contact support immediately.
            </p>

            <div class="footer">
                <p>Best regards,<br>Farm Management System Team</p>
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
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def send_verification_email(admin_user, request=None):
    """
    Send email verification link to admin user.

    Args:
        admin_user: AdminUser instance
        request: Django request object (for building absolute URL)

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Create or get existing verification token
    verification = EmailVerification.objects.create(admin_user=admin_user)

    # Build verification URL
    if request:
        # Use request to build absolute URL
        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
        verification_url = f"{protocol}://{domain}/api/admin/verify-email?token={verification.token}"
    else:
        # Fallback to settings-based URL
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        verification_url = f"{base_url}/api/admin/verify-email?token={verification.token}"

    subject = "Email Verification - Farm Management System"

    message = f"""
Hello {admin_user.name or 'Admin'},

Welcome to the Farm Management System Admin Portal!

Please verify your email address by clicking the link below:

{verification_url}

This verification link is valid for 24 hours.

If you did not create this account, please ignore this email or contact support.

Best regards,
Farm Management System Team
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
            border-radius: 10px;
        }}
        .header {{
            background-color: #8B4513;
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
        .button {{
            display: inline-block;
            background-color: #8B4513;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            font-weight: bold;
        }}
        .button:hover {{
            background-color: #654321;
        }}
        .warning {{
            color: #d32f2f;
            font-size: 14px;
            margin-top: 20px;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #666;
        }}
        .link-text {{
            word-break: break-all;
            color: #8B4513;
            font-size: 12px;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Email Verification</h2>
        </div>
        <div class="content">
            <p>Hello <strong>{admin_user.name or 'Admin'}</strong>,</p>

            <p>Welcome to the <strong>Farm Management System Admin Portal</strong>!</p>

            <p>Please verify your email address to complete your registration and access all features.</p>

            <div style="text-align: center;">
                <a href="{verification_url}" class="button">Verify Email Address</a>
            </div>

            <p class="link-text">Or copy and paste this link in your browser:<br>{verification_url}</p>

            <p><strong>This verification link is valid for 24 hours.</strong></p>

            <p class="warning">
                ⚠️ If you did not create this account, please ignore this email or contact support immediately.
            </p>

            <div class="footer">
                <p>Best regards,<br>Farm Management System Team</p>
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
            recipient_list=[admin_user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending verification email: {str(e)}")
        return False
