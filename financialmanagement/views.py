from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from .models import Balancesheet, Wage
from .serializers import WageSerializer, SaleSerializer, ExpenseSerializer, BalancesheetSerializer, StaffSerializer, SetpriceSerializer
from .models import Sale, Expense, Staff   
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from datetime import datetime
from users.permissions import IsSuperAdmin

# Create your views here.
class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [AllowAny]

class WageViewSet(viewsets.ModelViewSet):
    queryset = Wage.objects.all().select_related('staff').order_by('-date_of_payment')
    serializer_class = WageSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Create a new wage payment record
        Accepts employee_name as free text
        Optionally links to staff if staff_id is provided in 'staff' field
        """
        employee_name = request.data.get('employee_name')

        if not employee_name:
            return Response(
                {'error': 'Employee name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            wage_data = {
                'employee_name': employee_name,
                'date_of_payment': request.data.get('date_of_payment'),
                'days_missed': int(request.data.get('days_missed', 0)),
                'amount_paid': float(request.data.get('amount_paid', 0)),
            }

            # Optional: if a staff field is provided, link to registered staff
            staff_id = request.data.get('staff')
            if staff_id:
                try:
                    staff = Staff.objects.get(staff_id=staff_id)
                    wage_data['staff'] = staff.staff_id
                except Staff.DoesNotExist:
                    pass  # Just ignore if staff not found, still create the wage record

            serializer = self.get_serializer(data=wage_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
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

        wages = self.queryset.filter(staff__staff_id=staff_id)
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

from .models import Setprice
from .serializers import SetpriceSerializer

class SetpriceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing price settings.
    Only one record is active at a time (latest record determines current price).
    """
    queryset = Setprice.objects.all().order_by('-id')
    serializer_class = SetpriceSerializer
    permission_classes = [IsSuperAdmin]  # You can later restrict this to admins only

    def get_permissions(self):
        """
        Allow anyone to read prices (GET, retrieve, list, current),
        but only SuperAdmins can create/update/delete.
        """
        if self.action in ['list', 'retrieve', 'current']:
            return [AllowAny()]
        return [IsSuperAdmin()]

    def create(self, request, *args, **kwargs):
        """
        Custom create: add a new price record.
        The latest entry always represents the prevailing price.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Retrieve the current active price (the most recent Setprice entry).
        Usage: GET /api/setprice/current/
        """
        current_price = Setprice.objects.order_by('-id').first()
        if current_price:
            serializer = self.get_serializer(current_price)
            return Response(serializer.data)
        return Response({"detail": "No price has been set yet."}, status=404)