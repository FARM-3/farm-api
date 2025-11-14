# adminuser/views.py
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.utils import timezone
from .models import AdminUser, PasswordResetOTP
from .serializers import (
    AdminUserSerializer,
    AdminLoginSerializer,
    RequestPasswordResetSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer
)
from .utils import send_otp_email


# ============================================
# ADMIN LOGIN VIEW
# ============================================
@extend_schema(
    request=AdminLoginSerializer,
    responses={200: OpenApiResponse(description="Admin login successful")}
)
@api_view(['POST'])
@permission_classes([AllowAny])  # Anyone can attempt login
def admin_login_view(request):
    """
    API endpoint for admin user login.

    Endpoint: POST /api/adminuser/login/

    Request body:
        {
            "email": "admin@example.com",
            "password": "securepassword"
        }

    Response (success):
        {
            "message": "Login successful",
            "user": {
                "id": 1,
                "name": "Admin User",
                "email": "admin@example.com",
                "role": "admin",
                "role_display": "Admin"
            },
            "access": "eyJ0eXAiOiJKV1...",  # JWT token for auth
            "refresh": "eyJ0eXAiOiJKV1..."   # Refresh token
        }

    Response (failure):
        {
            "error": "Invalid email or password"
        }
    """

    # Step 1: Validate incoming data
    serializer = AdminLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 2: Extract validated data
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    # Step 3: Authenticate admin user
    # This uses our custom EmailPasswordBackend
    user = authenticate(request, username=email, password=password)

    if not user:
        return Response(
            {"error": "Invalid email or password"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {"error": "Account is disabled"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Step 4: Generate JWT tokens
    # Access token: short-lived, used for API requests
    # Refresh token: long-lived, used to get new access tokens
    refresh = RefreshToken.for_user(user)

    # Step 5: Return success response
    return Response({
        "message": "Login successful",
        "user": AdminUserSerializer(user).data,
        "access": str(refresh.access_token),  # Frontend stores this
        "refresh": str(refresh)
    }, status=status.HTTP_200_OK)


# ============================================
# ADMIN ME VIEW (Get current admin user info)
# ============================================
@extend_schema(
    responses={200: AdminUserSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_me_view(request):
    """
    Get current logged-in admin user's information.
    Requires JWT token in Authorization header.

    Endpoint: GET /api/adminuser/me/

    Headers:
        Authorization: Bearer <access_token>

    Response:
        {
            "id": 1,
            "name": "Admin User",
            "email": "admin@example.com",
            "role": "admin",
            "role_display": "Admin"
        }
    """

    # Check if the authenticated user is an AdminUser
    if not isinstance(request.user, AdminUser):
        return Response(
            {"error": "Access denied. Admin credentials required."},
            status=status.HTTP_403_FORBIDDEN
        )

    # request.user is automatically set by JWT authentication
    return Response(
        AdminUserSerializer(request.user).data,
        status=status.HTTP_200_OK
    )


# ============================================
# ADMIN LOGOUT VIEW
# ============================================
@extend_schema(
    responses={200: OpenApiResponse(description="Admin logout successful")},
    auth=[{'Bearer': []}]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_logout_view(request):
    """
    Logout endpoint for admin users - terminates session

    Endpoint: POST /api/adminuser/logout/

    Headers:
        Authorization: Bearer <access_token>

    Response (success):
        {
            "success": true,
            "message": "Successfully logged out"
        }
    """
    try:
        # For JWT, we don't need to do much on logout
        # The frontend should delete the token
        # If using token blacklist, you can blacklist the refresh token here

        return Response({
            'success': True,
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Logout failed: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# REQUEST PASSWORD RESET VIEW (Step 1: Request OTP)
# ============================================
@extend_schema(
    request=RequestPasswordResetSerializer,
    responses={200: OpenApiResponse(description="OTP sent to email")}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset_view(request):
    """
    Request password reset - sends OTP to admin's email.

    Endpoint: POST /api/adminuser/request-password-reset/

    Request body:
        {
            "email": "admin@example.com"
        }

    Response (success):
        {
            "message": "OTP has been sent to your email. Please check your inbox.",
            "email": "admin@example.com"
        }

    Response (failure):
        {
            "error": "Admin user with this email not found"
        }
    """

    # Step 1: Validate request
    serializer = RequestPasswordResetSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    email = serializer.validated_data['email']

    # Step 2: Check if admin user exists
    try:
        admin_user = AdminUser.objects.get(email=email)
    except AdminUser.DoesNotExist:
        return Response(
            {"error": "Admin user with this email not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Step 3: Invalidate any previous unused OTPs for this user
    PasswordResetOTP.objects.filter(
        admin_user=admin_user,
        is_used=False
    ).update(is_used=True)

    # Step 4: Create new OTP
    otp = PasswordResetOTP.objects.create(admin_user=admin_user)

    # Step 5: Send OTP via email
    email_sent = send_otp_email(
        email=admin_user.email,
        otp_code=otp.otp_code,
        admin_name=admin_user.name or "Admin"
    )

    if not email_sent:
        return Response(
            {"error": "Failed to send email. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Step 6: Return success response
    return Response({
        "message": "OTP has been sent to your email. Please check your inbox.",
        "email": email
    }, status=status.HTTP_200_OK)


# ============================================
# VERIFY OTP VIEW (Step 2: Verify OTP)
# ============================================
@extend_schema(
    request=VerifyOTPSerializer,
    responses={200: OpenApiResponse(description="OTP verified successfully")}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_view(request):
    """
    Verify OTP code before password reset.

    Endpoint: POST /api/adminuser/verify-otp/

    Request body:
        {
            "email": "admin@example.com",
            "otp_code": "123456"
        }

    Response (success):
        {
            "message": "OTP verified successfully. You can now reset your password.",
            "verified": true
        }

    Response (failure):
        {
            "error": "Invalid or expired OTP"
        }
    """

    # Step 1: Validate request
    serializer = VerifyOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    email = serializer.validated_data['email']
    otp_code = serializer.validated_data['otp_code']

    # Step 2: Find admin user
    try:
        admin_user = AdminUser.objects.get(email=email)
    except AdminUser.DoesNotExist:
        return Response(
            {"error": "Admin user not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Step 3: Find matching OTP
    try:
        otp = PasswordResetOTP.objects.get(
            admin_user=admin_user,
            otp_code=otp_code,
            is_used=False
        )
    except PasswordResetOTP.DoesNotExist:
        return Response(
            {"error": "Invalid OTP code"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 4: Check if OTP is still valid (not expired)
    if not otp.is_valid():
        return Response(
            {"error": "OTP has expired. Please request a new one."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 5: Mark OTP as verified
    otp.is_verified = True
    otp.save()

    # Step 6: Return success response
    return Response({
        "message": "OTP verified successfully. You can now reset your password.",
        "verified": True
    }, status=status.HTTP_200_OK)


# ============================================
# RESET PASSWORD VIEW (Step 3: Reset Password)
# ============================================
@extend_schema(
    request=ResetPasswordSerializer,
    responses={200: OpenApiResponse(description="Password reset successful")}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_view(request):
    """
    Reset password after OTP verification.

    Endpoint: POST /api/adminuser/reset-password/

    Request body:
        {
            "email": "admin@example.com",
            "otp_code": "123456",
            "new_password": "newsecurepassword",
            "confirm_password": "newsecurepassword"
        }

    Response (success):
        {
            "message": "Password reset successful. You can now login with your new password."
        }

    Response (failure):
        {
            "error": "Invalid or expired OTP"
        }
    """

    # Step 1: Validate request
    serializer = ResetPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    email = serializer.validated_data['email']
    otp_code = serializer.validated_data['otp_code']
    new_password = serializer.validated_data['new_password']

    # Step 2: Find admin user
    try:
        admin_user = AdminUser.objects.get(email=email)
    except AdminUser.DoesNotExist:
        return Response(
            {"error": "Admin user not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Step 3: Find and verify OTP
    try:
        otp = PasswordResetOTP.objects.get(
            admin_user=admin_user,
            otp_code=otp_code,
            is_verified=True,
            is_used=False
        )
    except PasswordResetOTP.DoesNotExist:
        return Response(
            {"error": "Invalid or unverified OTP. Please verify OTP first."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 4: Check if OTP is still valid (not expired)
    if not otp.is_valid():
        return Response(
            {"error": "OTP has expired. Please request a new one."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 5: Reset password
    admin_user.set_password(new_password)
    admin_user.save()

    # Step 6: Mark OTP as used
    otp.mark_as_used()

    # Step 7: Return success response
    return Response({
        "message": "Password reset successful. You can now login with your new password."
    }, status=status.HTTP_200_OK)
