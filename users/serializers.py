# users/serializers.py
from rest_framework import serializers
from .models import User, SecurityQuestion, UserSecurityAnswer
import re


# ============================================
# USER SERIALIZER (for returning user data)
# ============================================
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Used to return user information in API responses.
    NEVER includes sensitive data like PIN or security answer.
    """

    # Make role human-readable (e.g., "Farm Manager" instead of "manager")
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'name',
            'phone',
            'role',
            'role_display',
            'security_question',  # Question is OK to show, answer is NOT
            'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# ============================================
# LOGIN SERIALIZER
# ============================================
class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Validates phone number and PIN format.
    """
    
    phone = serializers.CharField(
        required=True,
        help_text="User's phone number"
    )
    
    pin = serializers.CharField(
        required=True,
        write_only=True,  # Never include PIN in response
        min_length=4,
        max_length=4,
        help_text="4-digit PIN"
    )
    
    def validate_pin(self, value):
        """
        Ensure PIN is exactly 4 numeric digits.
        
        Args:
            value (str): The PIN to validate
        
        Returns:
            str: Validated PIN
        
        Raises:
            ValidationError: If PIN is not 4 digits
        """
        if not re.match(r'^\d{4}$', value):
            raise serializers.ValidationError(
                "PIN must be exactly 4 numeric digits"
            )
        return value


# ============================================
# RESET PIN SERIALIZER
# ============================================
class ResetPinSerializer(serializers.Serializer):
    """
    Serializer for PIN reset using security question.
    User must provide correct security answer to reset PIN.
    """
    
    phone = serializers.CharField(
        required=True,
        help_text="User's phone number"
    )
    
    security_answer = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Answer to security question"
    )
    
    new_pin = serializers.CharField(
        required=True,
        write_only=True,
        min_length=4,
        max_length=4,
        help_text="New 4-digit PIN"
    )
    
    def validate_new_pin(self, value):
        """
        Ensure new PIN is exactly 4 numeric digits.
        
        Args:
            value (str): The new PIN to validate
        
        Returns:
            str: Validated PIN
        
        Raises:
            ValidationError: If PIN is not 4 digits
        """
        if not re.match(r'^\d{4}$', value):
            raise serializers.ValidationError(
                "PIN must be exactly 4 numeric digits"
            )
        return value
    
    def validate_security_answer(self, value):
        """
        Basic validation for security answer.
        Make it case-insensitive and strip whitespace.
        
        Args:
            value (str): The security answer
        
        Returns:
            str: Cleaned security answer
        """
        # Clean up the answer (lowercase, no extra spaces)
        return value.strip().lower()


# ============================================
# GET SECURITY QUESTION SERIALIZER
# ============================================
class SecurityQuestionSerializer(serializers.Serializer):
    """
    Serializer for retrieving a user's security question.
    Used before PIN reset so user knows what question to answer.
    """

    phone = serializers.CharField(
        required=True,
        help_text="User's phone number"
    )


# ============================================
# SECURITY QUESTION MODEL SERIALIZER
# ============================================
class SecurityQuestionModelSerializer(serializers.ModelSerializer):
    """
    Serializer for SecurityQuestion model.
    Used to return security questions for first login setup.
    """

    class Meta:
        model = SecurityQuestion
        fields = ['id', 'text']
        read_only_fields = ['id', 'text']


# ============================================
# SETUP SECURITY ANSWERS SERIALIZER
# ============================================
class SetupSecurityAnswersSerializer(serializers.Serializer):
    """
    Serializer for setting up security answers during first login.
    User receives 3 random questions and must answer all of them.
    """

    phone = serializers.CharField(
        required=True,
        help_text="User's phone number"
    )

    answers = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
            help_text="Dict with 'question_id' and 'answer' keys"
        ),
        help_text="List of {question_id, answer} pairs"
    )

    def validate_answers(self, value):
        """
        Validate that exactly 3 answers are provided.
        """
        if len(value) != 3:
            raise serializers.ValidationError(
                f"Must provide exactly 3 answers, got {len(value)}"
            )

        # Validate each answer has required fields
        for idx, answer_dict in enumerate(value):
            if 'question_id' not in answer_dict:
                raise serializers.ValidationError(
                    f"Answer {idx + 1} missing 'question_id'"
                )
            if 'answer' not in answer_dict:
                raise serializers.ValidationError(
                    f"Answer {idx + 1} missing 'answer'"
                )

            # Normalize and validate answer text
            answer_dict['answer'] = answer_dict['answer'].strip().lower()

        return value


# ============================================
# VERIFY SECURITY ANSWERS SERIALIZER (for PIN reset)
# ============================================
class VerifySecurityAnswersSerializer(serializers.Serializer):
    """
    Serializer for verifying security answers during PIN reset.
    User must answer all 3 security questions correctly.
    """

    phone = serializers.CharField(
        required=True,
        help_text="User's phone number"
    )

    answers = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
            help_text="Dict with 'question_id' and 'answer' keys"
        ),
        help_text="List of {question_id, answer} pairs"
    )

    new_pin = serializers.CharField(
        required=True,
        write_only=True,
        min_length=4,
        max_length=4,
        help_text="New 4-digit PIN"
    )

    def validate_answers(self, value):
        """
        Validate that exactly 3 answers are provided.
        """
        if len(value) != 3:
            raise serializers.ValidationError(
                f"Must provide exactly 3 answers, got {len(value)}"
            )

        for idx, answer_dict in enumerate(value):
            if 'question_id' not in answer_dict:
                raise serializers.ValidationError(
                    f"Answer {idx + 1} missing 'question_id'"
                )
            if 'answer' not in answer_dict:
                raise serializers.ValidationError(
                    f"Answer {idx + 1} missing 'answer'"
                )

            # Normalize answer
            answer_dict['answer'] = answer_dict['answer'].strip().lower()

        return value

    def validate_new_pin(self, value):
        """
        Ensure new PIN is exactly 4 numeric digits.
        """
        if not re.match(r'^\d{4}$', value):
            raise serializers.ValidationError(
                "PIN must be exactly 4 numeric digits"
            )
        return value