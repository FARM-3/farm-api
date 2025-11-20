from rest_framework import serializers
from .models import Fermenting, Washing, NaturalSundrying, Drying, Bagging, Ripeness, Floating

class FermentingSerializer(serializers.ModelSerializer):
    """
    Serializer for Fermenting model
    Processing ID and days are auto-calculated
    """
    # Read-only fields - auto-generated
    processing_id = serializers.ReadOnlyField()
    days = serializers.ReadOnlyField()

    # Display grade_id string instead of full object
    grade_id = serializers.CharField(source='grade.grade_id', read_only=True)

    class Meta:
        model = Fermenting
        fields = [
            'processing_id',  # Auto-generated, read-only
            'grade',  # For creating (accepts grade_id)
            'grade_id',  # For display (shows grade_id string)
            'start_date',
            'end_date',
            'days',  # Auto-calculated, read-only
            'weight',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['processing_id', 'days', 'created_at', 'updated_at']

    def validate(self, attrs):
        """
        Validate that end_date is after start_date
        """
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if start_date and end_date:
            if end_date < start_date:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date'
                })

        return attrs

class WashingSerializer(serializers.ModelSerializer):
    """
    Serializer for Washing model
    Processing ID is auto-generated
    """
    # Read-only field - auto-generated
    processing_id = serializers.ReadOnlyField()

    # Display grade_id string instead of full object
    grade_id = serializers.CharField(source='grade.grade_id', read_only=True)

    class Meta:
        model = Washing
        fields = [
            'processing_id',  # Auto-generated, read-only
            'grade',  # For creating (accepts grade_id)
            'grade_id',  # For display (shows grade_id string)
            'date',
            'weight',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['processing_id', 'created_at', 'updated_at']


class NaturalSundryingSerializer(serializers.ModelSerializer):
    """
    Serializer for NaturalSundrying model
    Processing ID is auto-generated
    """
    # Read-only field - auto-generated
    processing_id = serializers.ReadOnlyField()

    # Display grade_id string instead of full object
    grade_id = serializers.CharField(source='grade.grade_id', read_only=True)

    class Meta:
        model = NaturalSundrying
        fields = [
            'processing_id',  # Auto-generated, read-only
            'grade',  # For creating (accepts grade_id)
            'grade_id',  # For display (shows grade_id string)
            'start_date',
            'weight',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['processing_id', 'created_at', 'updated_at']     
    

class DryingSerializer(serializers.ModelSerializer):
    """
    Serializer for Drying model (Offline-First Approach)
    Frontend handles ALL calculations and business logic
    Backend simply stores and retrieves data
    """

    class Meta:
        model = Drying
        fields = [
            'id',
            # User-provided fields
            'processing_id',
            'lot_id',
            'date',
            'weather_condition',
            'moisture_content',
            'weight',
            'moisture_before',
            'weight_before',
            # Calculated fields (now writable - calculated on frontend)
            'processing_type',
            'type_of_coffee',
            'days',
            'moisture_deviation',
            'rate_of_drying',
            'rate_of_weightloss',
            'outturn',
            'outturn_deviation',
            # Metadata
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_moisture_content(self, value):
        """
        Validate that moisture content is in valid range
        """
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Moisture content must be between 0 and 100%"
            )
        return value
    
class BaggingSerializer(serializers.ModelSerializer):
    """
    Serializer for Bagging model (final stage)
    """
    class Meta:
        model = Bagging
        fields = [
            'id',
            'processing_id',
            'name',
            'grade',
            'moisture_content',
            'date',
            'weight',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_moisture_content(self, value):
        """
        Validate that moisture content is in acceptable range for bagging
        Typically, coffee should be dried to 10-12% moisture before bagging
        """
        if value > 15:
            raise serializers.ValidationError(
                "Moisture content too high for bagging (should be ≤15%)"
            )
        if value < 8:
            raise serializers.ValidationError(
                "Moisture content too low (should be ≥8%)"
            )
        return value


class RipenessSerializer(serializers.ModelSerializer):
    """
    Serializer for Ripeness (Quality Control) model
    Ripeness score is auto-calculated by the model's save() method
    """
    # Read-only field - calculated automatically from no_of_redcherry / sample_size
    ripeness_score = serializers.ReadOnlyField()

    # Display harvest_id instead of the full harvest object
    harvest_id = serializers.CharField(source='harvest.harvest_id', read_only=True)

    class Meta:
        model = Ripeness
        fields = [
            'harvest',  # For creating/updating (accepts harvest_id)
            'harvest_id',  # For display (shows harvest_id string)
            'date',
            'sample_size',
            'no_of_redcherry',
            'ripeness_score',  # Auto-calculated, read-only
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['ripeness_score', 'created_at', 'updated_at']

    def validate(self, attrs):
        """
        Custom validation to ensure no_of_redcherry doesn't exceed sample_size
        """
        no_of_redcherry = attrs.get('no_of_redcherry')
        sample_size = attrs.get('sample_size')

        # If both values are provided, validate
        if no_of_redcherry is not None and sample_size is not None:
            if no_of_redcherry > sample_size:
                raise serializers.ValidationError({
                    'no_of_redcherry': f'Number of red cherries ({no_of_redcherry}) cannot exceed sample size ({sample_size})'
                })

        return attrs


class FloatingSerializer(serializers.ModelSerializer):
    """
    Serializer for Floating (Quality Control) model
    Grade ID is auto-generated by the model's save() method
    Ripeness score is auto-filled from the related Ripeness test
    """
    # Read-only fields - auto-generated/auto-filled
    grade_id = serializers.ReadOnlyField()
    ripeness_score = serializers.ReadOnlyField()

    # Display harvest_id instead of the full harvest object
    harvest_id = serializers.CharField(source='harvest.harvest_id', read_only=True)

    class Meta:
        model = Floating
        fields = [
            'grade_id',  # Auto-generated (e.g., GRA1411A00), read-only
            'harvest',  # For creating/updating (accepts harvest_id)
            'harvest_id',  # For display (shows harvest_id string)
            'grade',  # User input (e.g., "A" or "B")
            'weight',
            'date',
            'ripeness_score',  # Auto-filled from Ripeness test, read-only
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['grade_id', 'ripeness_score', 'created_at', 'updated_at']

    def validate_grade(self, value):
        """
        Optional validation for grade field
        Frontend handles choices, but we can validate the format
        """
        if not value or len(value) == 0:
            raise serializers.ValidationError("Grade cannot be empty")
        return value


