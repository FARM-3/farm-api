from django.shortcuts import render

# Create your views here.
# users/views.py
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import User
from .serializers import (
    UserSerializer,
    LoginSerializer,
    ResetPinSerializer,
    SecurityQuestionSerializer
)


# ============================================
# LOGIN VIEW
# ============================================
@extend_schema(
    request=LoginSerializer,
    responses={200: OpenApiResponse(description="Login successful")}
)
@api_view(['POST'])
@permission_classes([AllowAny])  # Anyone can attempt login
def login_view(request):
    """
    API endpoint for user login.
    
    Endpoint: POST /api/users/login/
    
    Request body:
        {
            "phone": "0700000000",
            "pin": "1234"
        }
    
    Response (success):
        {
            "message": "Login successful",
            "user": {
                "id": 1,
                "name": "John Doe",
                "phone": "0700000000",
                "role": "manager",
                "role_display": "Farm Manager"
            },
            "access": "eyJ0eXAiOiJKV1...",  # JWT token for auth
            "refresh": "eyJ0eXAiOiJKV1..."   # Refresh token
        }
    
    Response (failure):
        {
            "error": "Invalid phone number or PIN"
        }
    """
    
    # Step 1: Validate incoming data
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Step 2: Extract validated data
    phone = serializer.validated_data['phone']
    pin = serializer.validated_data['pin']
    
    # Step 3: Authenticate user
    # This uses our custom PhonePinBackend
    user = authenticate(request, username=phone, password=pin)
    
    if not user:
        return Response(
            {"error": "Invalid phone number or PIN"},
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
        "user": UserSerializer(user).data,
        "access": str(refresh.access_token),  # Frontend stores this
        "refresh": str(refresh)
    }, status=status.HTTP_200_OK)


# ============================================
# GET SECURITY QUESTION VIEW
# ============================================
@extend_schema(
    request=SecurityQuestionSerializer,
    responses={200: OpenApiResponse(description="Security question retrieved")}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def get_security_question_view(request):
    """
    Get user's security question (needed before PIN reset).
    
    Endpoint: POST /api/users/security-question/
    
    Request body:
        {
            "phone": "0700000000"
        }
    
    Response (success):
        {
            "phone": "0700000000",
            "security_question": "What is your mother's name?"
        }
    
    Response (failure):
        {
            "error": "User not found"
        }
    """
    
    # Step 1: Validate request
    serializer = SecurityQuestionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    phone = serializer.validated_data['phone']
    
    # Step 2: Find user
    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Step 3: Check if user has security question
    if not user.security_question:
        return Response(
            {"error": "No security question set. Contact admin."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Step 4: Return question (NOT the answer!)
    return Response({
        "phone": user.phone,
        "security_question": user.security_question
    }, status=status.HTTP_200_OK)


# ============================================
# RESET PIN VIEW
# ============================================
@extend_schema(
    request=ResetPinSerializer,
    responses={200: OpenApiResponse(description="PIN reset successful")}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_pin_view(request):
    """
    Reset user's PIN using security question.
    
    Endpoint: POST /api/users/reset-pin/
    
    Request body:
        {
            "phone": "0700000000",
            "security_answer": "maria",
            "new_pin": "5678"
        }
    
    Response (success):
        {
            "message": "PIN reset successful. You can now login with your new PIN."
        }
    
    Response (failure):
        {
            "error": "Incorrect security answer"
        }
    """
    
    # Step 1: Validate request data
    serializer = ResetPinSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Step 2: Extract validated data
    phone = serializer.validated_data['phone']
    security_answer = serializer.validated_data['security_answer']
    new_pin = serializer.validated_data['new_pin']
    
    # Step 3: Find user
    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Step 4: Verify security answer
    # Convert stored answer to lowercase for comparison
    if not user.check_security_answer(security_answer):
        return Response(
            {"error": "Incorrect security answer"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Step 5: Update PIN
    user.set_password(new_pin)  # Hash and save new PIN
    user.save()
    
    # Step 6: Return success
    return Response({
        "message": "PIN reset successful. You can now login with your new PIN."
    }, status=status.HTTP_200_OK)


# ============================================
# ME VIEW (Get current user info)
# ============================================
@api_view(['GET'])
# Note: This view requires authentication (JWT token in header)
def me_view(request):
    """
    Get current logged-in user's information.
    Requires JWT token in Authorization header.
    
    Endpoint: GET /api/users/me/
    
    Headers:
        Authorization: Bearer <access_token>
    
    Response:
        {
            "id": 1,
            "name": "John Doe",
            "phone": "0700000000",
            "role": "manager",
            "role_display": "Farm Manager"
        }
    """
    
    # request.user is automatically set by JWT authentication
    return Response(
        UserSerializer(request.user).data,
        status=status.HTTP_200_OK
    )