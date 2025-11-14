# adminuser/utils.py
from django.core.mail import send_mail
from django.conf import settings


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
