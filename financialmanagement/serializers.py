from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Sale, Wage, Expense, Balancesheet, Staff

class StaffSerializer(serializers.ModelSerializer):
    """
    Serializer for Staff model
    Handles serialization/deserialization of staff data
    """
    
    # Read-only field to display full name
    full_name = serializers.SerializerMethodField()
    
    # Read-only field to display full address
    full_address = serializers.SerializerMethodField()
    
    # Staff ID is auto-generated and read-only
    staff_id = serializers.CharField(read_only=True)
    
    class Meta:
        model = Staff
        fields = '__all__'
        read_only_fields = ['staff_id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        """
        Return the staff member's full name
        """
        return obj.get_full_name()
    
    def get_full_address(self, obj):
        """
        Return the staff member's complete address
        """
        return obj.get_full_address()
    
    def validate_nin(self, value):
        """
        Validate NIN format - ensure it's uppercase
        """
        return value.upper()
    
    def validate(self, data):
        """
        Object-level validation
        """
        # Ensure date_hired is not in the future
        if 'date_hired' in data:
            from django.utils import timezone
            if data['date_hired'] > timezone.now().date():
                raise serializers.ValidationError({
                    'date_hired': 'Date hired cannot be in the future'
                })
        
        return data
     


class WageSerializer(serializers.ModelSerializer):
    # Use SlugRelatedField so clients can post the staff's `staff_id` (a string)
    # PrimaryKeyRelatedField's `pk_field` expects a Field instance, not a string,
    # which caused the "'str' object has no attribute 'to_internal_value'" error.
    employee_name = serializers.SlugRelatedField(
        queryset=Staff.objects.filter(is_active=True),
        slug_field='staff_id',
        label="Staff ID",
        help_text="The unique ID of the active staff member (e.g., RF001)"
    )
    employee_display = serializers.SerializerMethodField(read_only=True)
    staff_id = serializers.SerializerMethodField(read_only=True)
    net_salary = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = Wage
        fields = (
            'id', 
            'employee_name',
            'employee_display',
            'staff_id', 
            'days_worked', 
            'amount_paid', 
            'date_of_payment', 
            'monthly_pay', 
            'deduction', 
            'noted_reason', 
            'net_salary'  
        )

        read_only_fields = ('net_salary', 'employee_display', 'staff_id')

    def get_employee_display(self, obj):
        # Support both: employee_name can be a Staff instance or a plain string
        emp = obj.employee_name
        if not emp:
            return ""
        # If it's a Staff instance (has staff_id and name attrs)
        if hasattr(emp, 'staff_id'):
            first = getattr(emp, 'first_name', '')
            last = getattr(emp, 'last_name', '')
            return f"{emp.staff_id} - {first} {last}".strip()
        # Otherwise just return the string representation
        return str(emp)
    
    def get_staff_id(self, obj):
        """
        Return just the staff_id for easy reference
        """
        emp = obj.employee_name
        if not emp:
            return None
        return getattr(emp, 'staff_id', None)
    
    def get_net_salary(self, obj):
        """
        Calculate net salary (amount_paid - deduction)
        """
        # Use the model property if available, otherwise compute safely
        try:
            if hasattr(obj, 'calculate_net_salary'):
                return obj.calculate_net_salary
        except Exception:
            pass
        return (obj.amount_paid or 0) - (obj.deduction or 0)
    
    def to_representation(self, instance):
        """
        Customize the output representation
        Override employee_name to show display format instead of ID
        """
        representation = super().to_representation(instance)
        # Replace employee_name with the display format in responses
        representation['employee_name'] = self.get_employee_display(instance)
        return representation
    
    def validate_days_worked(self, value):
        """
        Validate days_worked is positive
        """
        if value < 0:
            raise serializers.ValidationError("Days worked cannot be negative")
        if value > 31:
            raise serializers.ValidationError("Days worked cannot exceed 31 days")
        return value
    
    def validate_amount_paid(self, value):
        """
        Validate amount_paid is positive
        """
        if value < 0:
            raise serializers.ValidationError("Amount paid cannot be negative")
        return value
    
    def validate_deduction(self, value):
        """
        Validate deduction is not negative
        """
        if value < 0:
            raise serializers.ValidationError("Deduction cannot be negative")
        return value
    
    def validate(self, data):
        """
        Object-level validation
        """
        # Ensure date_of_payment is not in the future
        if 'date_of_payment' in data:
            from django.utils import timezone
            if data['date_of_payment'] > timezone.now().date():
                raise serializers.ValidationError({
                    'date_of_payment': 'Payment date cannot be in the future'
                })
        amount_paid = data.get('amount_paid', 0)
        deduction = data.get('deduction', 0)
        if deduction > amount_paid:
            raise serializers.ValidationError({
                'deduction': 'Deduction cannot exceed amount paid'
            })
        
        return data


class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = [
            'id', 'customer_name', 'item', 'rate', 'quantity', 
            'total_amount', 'amount', 'date_of_payment', 
            'status', 'balance', 'method_of_payment'
        ]
    
        read_only_fields = ['total_amount', 'status', 'balance']

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'


class BalancesheetSerializer(serializers.ModelSerializer):
    # This field shows the full category name (e.g., "Asset")
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)

    class Meta:
        model = Balancesheet
        fields = ['id', 'account_name', 'account_type', 'account_type_display', 'balance', 'last_updated']
        read_only_fields = ['last_updated']



class StaffSerializer(serializers.ModelSerializer):
    """
    Serializer for Staff model
    Handles serialization/deserialization of staff data
    """
    
    # Read-only field to display full name
    full_name = serializers.SerializerMethodField()
    
    # Read-only field to display full address
    full_address = serializers.SerializerMethodField()
    
    # Staff ID is auto-generated and read-only
    staff_id = serializers.CharField(read_only=True)
    
    class Meta:
        model = Staff
        fields = '__all__'
        read_only_fields = ['staff_id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        """
        Return the staff member's full name
        """
        return obj.get_full_name()
    
    def get_full_address(self, obj):
        """
        Return the staff member's complete address
        """
        return obj.get_full_address()
    
    def validate_nin(self, value):
        """
        Validate NIN format - ensure it's uppercase
        """
        return value.upper()
    
    def validate(self, data):
        """
        Object-level validation
        """
        # Ensure date_hired is not in the future
        if 'date_hired' in data:
            from django.utils import timezone
            if data['date_hired'] > timezone.now().date():
                raise serializers.ValidationError({
                    'date_hired': 'Date hired cannot be in the future'
                })
        
        return data


class StaffListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing staff members
    Shows only essential information
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Staff
        fields = ['staff_id', 'full_name', 'nin', 'employment_type', 'is_active']
    
    def get_full_name(self, obj):
        return obj.get_full_name()