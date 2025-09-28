from rest_framework import serializers
from .models import Wage

class WageSerializer(serializers.ModelSerializer):
    net_salary = serializers.ReadOnlyField(source='calculate_net_salary')

    class Meta:
        model = Wage
        fields = (
            'id', 
            'employee_name', 
            'days_worked', 
            'amount_paid', 
            'date_of_payment', 
            'monthly_pay', 
            'deduction', 
            'noted_reason', 
            'net_salary'  # The calculated field
        )
        # Users can't manually set the net salary, it is always calculated.
        read_only_fields = ('net_salary',)
