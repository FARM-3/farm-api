from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from .models import Balancesheet, Wage
from .serializers import WageSerializer, SaleSerializer, ExpenseSerializer, BalancesheetSerializer, StaffSerializer
from .models import Sale, Expense, Staff   
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from datetime import datetime

# Create your views here.
class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [AllowAny]

class WageViewSet(viewsets.ModelViewSet):
    queryset = Wage.objects.all().select_related('employee_name').order_by('-date_of_payment')
    serializer_class = WageSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Create a new wage payment record
        Expects staff_id in employee_name field
        """
        staff_id = request.data.get('employee_name')
        
        if not staff_id:
            return Response(
                {'error': 'Employee name (staff_id) is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get the staff instance
            staff = Staff.objects.get(staff_id=staff_id)
            wage_data = {
                # Staff model uses `staff_id` as the primary key (to_field on Wage),
                # so pass that value when creating a Wage record.
                'employee_name': staff.staff_id,
                'date_of_payment': request.data.get('date_of_payment'),
                'days_worked': int(request.data.get('days_worked', 0)),
                'monthly_pay': int(request.data.get('monthly_pay')) if request.data.get('monthly_pay') else None,
                'amount_paid': int(request.data.get('amount_paid', 0)),
                'deduction': int(request.data.get('deduction', 0)),
                'noted_reason': request.data.get('noted_reason', ''),
            }
            serializer = self.get_serializer(data=wage_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED, 
                headers=headers
            )
            
        except Staff.DoesNotExist:
            return Response(
                {'error': f'Staff member with ID {staff_id} not found or inactive'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response(
                {'error': f'Invalid number format: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    @action(detail=False, methods=['get'])
    def by_employee(self, request):
        """
        Get wages filtered by employee staff_id
        Usage: /wages/by_employee/?staff_id=RF001
        """
        staff_id = request.query_params.get('staff_id')
        if not staff_id:
            return Response(
                {'error': 'staff_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        wages = self.queryset.filter(employee_name__staff_id=staff_id)
        serializer = self.get_serializer(wages, many=True)
        return Response(serializer.data)
        
class SaleViewSet(viewsets.ModelViewSet):

    queryset = Sale.objects.all().order_by('-date_of_payment', 'customer_name')
    serializer_class = SaleSerializer
    permission_classes = [AllowAny]

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [AllowAny]

class BalanceSheetViewSet(viewsets.ModelViewSet):
    queryset = Balancesheet.objects.all()
    serializer_class = BalancesheetSerializer
    # Setting permission to AllowAny
    permission_classes = [AllowAny]

class FinancialSummaryView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, format=None):
        try:
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')

            # If no dates provided, return all-time summary
            if not start_date_str or not end_date_str:
                wage_data = Wage.objects.aggregate(total_wages=Sum('monthly_pay'))
                expense_data = Expense.objects.aggregate(total_expenses=Sum('amount'))
            else:
                # Parse dates
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

                wage_data = Wage.objects.filter(
                    date_of_payment__range=[start_date, end_date]
                ).aggregate(total_wages=Sum('monthly_pay'))
                
                expense_data = Expense.objects.filter(
                    date__range=[start_date, end_date]
                ).aggregate(total_expenses=Sum('amount'))

            total_wages = wage_data.get('total_wages') or 0
            total_expenses = expense_data.get('total_expenses') or 0
            total_costs = total_wages + total_expenses

            return Response({
                "start_date": start_date_str,
                "end_date": end_date_str,
                "total_wages": total_wages,
                "total_expenses": total_expenses,
                "total_costs": total_costs
            })
        except ValueError as e:
            return Response(
                {"error": "Invalid date format. Please use YYYY-MM-DD"},
                status=400
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=500
            )

        

