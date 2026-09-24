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
from django.contrib.auth import logout
from rest_framework.permissions import IsAuthenticated
from .models import User, SecurityQuestion, UserSecurityAnswer, LoginAudit
from .serializers import (
    UserSerializer,
    LoginSerializer,
    ResetPinSerializer,
    SecurityQuestionSerializer,
    SecurityQuestionModelSerializer,
    SetupSecurityAnswersSerializer,
    VerifySecurityAnswersSerializer
)
import random


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
    
    def _client_ip(req):
        xff = req.META.get('HTTP_X_FORWARDED_FOR')
        return xff.split(',')[0].strip() if xff else req.META.get('REMOTE_ADDR')

    if not user:
        LoginAudit.objects.create(
            phone=phone, success=False,
            ip_address=_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
        )
        return Response(
            {"error": "Invalid phone number or PIN"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {"error": "Account is disabled"},
            status=status.HTTP_403_FORBIDDEN
        )

    platform = request.data.get('platform', 'web')
    mobile_only_roles = {'block_champion'}
    if platform == 'web' and user.role in mobile_only_roles:
        LoginAudit.objects.create(
            user=user, phone=phone, success=False,
            ip_address=_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
        )
        return Response(
            {
                "error": "mobile_only",
                "message": (
                    "Block Champion accounts are registered for mobile access only. "
                    "Please use the FMIS mobile app to log in with these credentials."
                ),
            },
            status=status.HTTP_403_FORBIDDEN,
        )
    
    # Step 4: Generate JWT tokens
    # Access token: short-lived, used for API requests
    # Refresh token: long-lived, used to get new access tokens
    refresh = RefreshToken.for_user(user)

    LoginAudit.objects.create(
        user=user, phone=phone, success=True,
        ip_address=_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
    )
    
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
@extend_schema(
    responses={200: UserSerializer}
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Add this line!
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



@extend_schema(
    responses={200: OpenApiResponse(description="Logout successful")},
    auth=[{'Bearer': []}]
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout endpoint - terminates session and deletes token
    """
    try:
        # Delete the user's token
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()

        # Logout user
        logout(request)

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
# GET RANDOM SECURITY QUESTIONS VIEW
# ============================================
@extend_schema(
    responses={200: OpenApiResponse(description="3 random security questions")}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def get_random_security_questions_view(request):
    """
    Get 3 random security questions for first-time user setup.

    Endpoint: POST /api/users/random-security-questions/

    Request body:
        {
            "phone": "0700000000"
        }

    Response (success):
        {
            "questions": [
                {"id": 1, "text": "What was your mother's clan name?"},
                {"id": 3, "text": "Which year did you start coffee farming?"},
                {"id": 5, "text": "Who is your favourite musician?"}
            ]
        }

    Response (failure):
        {
            "error": "User not found"
        }
    """

    # Step 1: Validate phone number
    from rest_framework import serializers as drf_serializers
    phone = request.data.get('phone')

    if not phone:
        return Response(
            {"error": "Phone number is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 2: Verify user exists
    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Step 3: Get 3 random active security questions
    active_questions = SecurityQuestion.objects.filter(is_active=True)

    if active_questions.count() < 3:
        return Response(
            {"error": "Not enough security questions available. Contact admin."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Randomly select 3 questions
    random_questions = random.sample(list(active_questions), 3)

    # Step 4: Serialize and return
    serializer = SecurityQuestionModelSerializer(random_questions, many=True)
    return Response({
        "questions": serializer.data
    }, status=status.HTTP_200_OK)


# ============================================
# SETUP SECURITY ANSWERS VIEW (First Login)
# ============================================
@extend_schema(
    request=SetupSecurityAnswersSerializer,
    responses={200: OpenApiResponse(description="Security answers set successfully")}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def setup_security_answers_view(request):
    """
    User answers 3 security questions on first login and saves answers.

    Endpoint: POST /api/users/setup-security-answers/

    Request body:
        {
            "phone": "0700000000",
            "answers": [
                {"question_id": 1, "answer": "my mother's clan"},
                {"question_id": 3, "answer": "2010"},
                {"question_id": 5, "answer": "musician name"}
            ]
        }

    Response (success):
        {
            "message": "Security answers set successfully",
            "security_answers_set": true
        }

    Response (failure):
        {
            "error": "User not found"
        }
    """

    # Step 1: Validate request
    serializer = SetupSecurityAnswersSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 2: Extract validated data
    phone = serializer.validated_data['phone']
    answers = serializer.validated_data['answers']

    # Step 3: Find user
    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Step 4: Verify all question IDs exist and are active
    question_ids = [answer['question_id'] for answer in answers]
    try:
        questions = SecurityQuestion.objects.filter(
            id__in=question_ids,
            is_active=True
        )

        if questions.count() != len(question_ids):
            return Response(
                {"error": "One or more questions are invalid or inactive"},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        return Response(
            {"error": f"Error validating questions: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 5: Save answers for each question
    try:
        for answer_dict in answers:
            question_id = answer_dict['question_id']
            answer_text = answer_dict['answer']

            question = SecurityQuestion.objects.get(id=question_id)

            # Create or update the UserSecurityAnswer
            user_answer, created = UserSecurityAnswer.objects.update_or_create(
                user=user,
                question=question,
                defaults={'answer_hash': ''}  # Will be set below
            )

            # Hash and save the answer
            user_answer.set_answer(answer_text)
            user_answer.save()

        # Step 6: Mark security answers as set
        user.security_answers_set = True
        user.save()

        # Step 7: Return success
        return Response({
            "message": "Security answers set successfully",
            "security_answers_set": True
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": f"Error saving answers: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================
# GET USER'S SECURITY QUESTIONS FOR PIN RESET
# ============================================
@extend_schema(
    request=SecurityQuestionSerializer,
    responses={200: OpenApiResponse(description="User's security questions")}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def get_user_security_questions_view(request):
    """
    Get the specific 3 security questions that a user answered during first login.
    Used for PIN reset - user answers the SAME questions they set up initially.

    Endpoint: POST /api/users/user-security-questions/

    Request body:
        {
            "phone": "0700000000"
        }

    Response (success):
        {
            "questions": [
                {"id": 1, "text": "What was your mother's clan name?"},
                {"id": 3, "text": "Which year did you start coffee farming?"},
                {"id": 5, "text": "Who is your favourite musician?"}
            ]
        }

    Response (failure):
        {
            "error": "User not found" or "User has not set up security questions"
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

    # Step 3: Check if user has set up security answers
    if not user.security_answers_set:
        return Response(
            {"error": "User has not set up security questions yet"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 4: Get the user's specific security answers (not random)
    user_answers = UserSecurityAnswer.objects.filter(user=user)

    if user_answers.count() == 0:
        return Response(
            {"error": "No security questions found for this user"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 5: Return the QUESTIONS (not answers) that the user answered
    # Return only the first 3 for consistency with first-time login flow
    questions = []
    for answer_record in user_answers[:3]:  # Limit to first 3
        questions.append({
            "id": answer_record.question.id,
            "text": answer_record.question.text
        })

    return Response({
        "questions": questions
    }, status=status.HTTP_200_OK)


# ============================================
# VERIFY SECURITY ANSWERS VIEW (PIN Reset)
# ============================================
@extend_schema(
    request=VerifySecurityAnswersSerializer,
    responses={200: OpenApiResponse(description="PIN reset successful")}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_security_answers_and_reset_pin_view(request):
    """
    User verifies 3 security answers to reset their PIN.

    Endpoint: POST /api/users/verify-answers-reset-pin/

    Request body:
        {
            "phone": "0700000000",
            "answers": [
                {"question_id": 1, "answer": "my mother's clan"},
                {"question_id": 3, "answer": "2010"},
                {"question_id": 5, "answer": "musician name"}
            ],
            "new_pin": "5678"
        }

    Response (success):
        {
            "message": "PIN reset successful. You can now login with your new PIN."
        }

    Response (failure):
        {
            "error": "One or more answers are incorrect"
        }
    """

    # Step 1: Validate request
    serializer = VerifySecurityAnswersSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 2: Extract validated data
    phone = serializer.validated_data['phone']
    answers = serializer.validated_data['answers']
    new_pin = serializer.validated_data['new_pin']

    # Step 3: Find user
    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Step 4: Verify all answers
    for answer_dict in answers:
        question_id = answer_dict['question_id']
        answer_text = answer_dict['answer']

        try:
            question = SecurityQuestion.objects.get(id=question_id)
            user_answer = UserSecurityAnswer.objects.get(user=user, question=question)

            # Check if answer matches
            if not user_answer.check_answer(answer_text):
                return Response(
                    {"error": "One or more answers are incorrect"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        except (SecurityQuestion.DoesNotExist, UserSecurityAnswer.DoesNotExist):
            return Response(
                {"error": "Question or answer not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Step 5: All answers verified - reset PIN
    user.set_password(new_pin)
    user.save()

    # Step 6: Return success
    return Response({
        "message": "PIN reset successful. You can now login with your new PIN."
    }, status=status.HTTP_200_OK)