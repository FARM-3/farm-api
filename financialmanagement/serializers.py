from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Sale, Wage, Expense, Balancesheet, Staff, Setprice, Customer, Supplier

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
    # Optional fields for when linked to registered staff
    staff_id = serializers.CharField(source='staff.staff_id', read_only=True, allow_null=True)
    staff_full_name = serializers.CharField(source='staff.get_full_name', read_only=True, allow_null=True)

    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    

    class Meta:
        model = Wage
        fields = (
            'id',
            'employee_name',
            'staff',
            'staff_id',
            'staff_full_name',
            'days_missed',
            'amount_paid',
            'date_of_payment',
        )

        read_only_fields = ('staff_id', 'staff_full_name')

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ['customer_id', 'created_at']


class SaleSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    customer_id_display = serializers.CharField(source='customer.customer_id', read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'customer', 'customer_id_display', 'first_name', 'last_name', 'customer_name',
            'batch_id', 'item', 'rate', 'quantity',
            'total_amount', 'amount', 'date_of_payment',
            'status', 'balance', 'method_of_payment',
        ]

        read_only_fields = ['total_amount', 'status', 'balance', 'customer_name', 'customer_id_display']

    def create(self, validated_data):
        customer = validated_data.get('customer')
        if customer and not validated_data.get('first_name'):
            parts = customer.name.split(' ', 1)
            validated_data['first_name'] = parts[0]
            validated_data['last_name'] = parts[1] if len(parts) > 1 else ''
        return super().create(validated_data)

    def get_customer_name(self, obj):
        """Return the customer's full name for backward compatibility"""
        return obj.get_customer_name()

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

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ['supplier_id', 'created_at', 'updated_at']


class SetpriceSerializer(serializers.ModelSerializer):
    """
    Serializer for Setprice model
    Handles serialization/deserialization of price per KG for production and farmer
    """

    class Meta:
        model = Setprice
        fields = '__all__'  # Includes both prices and id
        read_only_fields = []  # All fields editable