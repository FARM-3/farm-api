from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from .models import Balancesheet, Wage
from .serializers import (
    WageSerializer, SaleSerializer, ExpenseSerializer, BalancesheetSerializer,
    StaffSerializer, SetpriceSerializer, CustomerSerializer, SupplierSerializer,
)
from .models import Sale, Expense, Staff, Customer, Supplier
from .bulk_import import download_template, parse_csv_upload, import_staff_rows, import_wage_rows
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from datetime import datetime
from users.permissions import IsSuperAdmin
from api.query_filters import apply_date_range, apply_exact, apply_icontains

# Create your views here.
class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = apply_exact(qs, self.request, 'employment_type')
        qs = apply_exact(qs, self.request, 'district')
        is_active = self.request.query_params.get('is_active')
        if is_active in ('true', 'false', '1', '0'):
            qs = qs.filter(is_active=is_active in ('true', '1'))
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                first_name__icontains=search
            ) | qs.filter(last_name__icontains=search)
        return qs.order_by('first_name', 'last_name')

    @action(detail=False, methods=['get'], url_path='import-template')
    def import_template(self, request):
        return download_template('staff')

    @action(detail=False, methods=['post'], url_path='bulk-import')
    def bulk_import(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'file required'}, status=status.HTTP_400_BAD_REQUEST)
        rows = parse_csv_upload(file)
        created, errors = import_staff_rows(rows)
        return Response({'created': created, 'errors': errors})


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.filter(is_active=True)
    serializer_class = SupplierSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Supplier.objects.all()
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)
        active = self.request.query_params.get('is_active')
        if active in ('true', 'false', '1', '0'):
            qs = qs.filter(is_active=active in ('true', '1'))
        elif self.action == 'list' and not self.request.query_params.get('include_inactive'):
            qs = qs.filter(is_active=True)
        return qs.order_by('name')


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.filter(is_active=True)
    serializer_class = CustomerSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

class WageViewSet(viewsets.ModelViewSet):
    queryset = Wage.objects.all().select_related('staff').order_by('-date_of_payment')
    serializer_class = WageSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = apply_date_range(qs, self.request, 'date_of_payment')
        staff_id = self.request.query_params.get('staff_id')
        if staff_id:
            qs = qs.filter(staff__staff_id=staff_id)
        return qs

    @action(detail=False, methods=['get'], url_path='import-template')
    def import_template(self, request):
        return download_template('wages')

    @action(detail=False, methods=['post'], url_path='bulk-import')
    def bulk_import(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'file required'}, status=status.HTTP_400_BAD_REQUEST)
        rows = parse_csv_upload(file)
        created, errors = import_wage_rows(rows)
        return Response({'created': created, 'errors': errors})

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

    queryset = Sale.objects.all().order_by('-date_of_payment', 'last_name', 'first_name')
    serializer_class = SaleSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = apply_date_range(qs, self.request, 'date_of_payment')
        qs = apply_exact(qs, self.request, 'item')
        qs = apply_exact(qs, self.request, 'method_of_payment')
        qs = apply_exact(qs, self.request, 'status')
        return qs

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = apply_date_range(qs, self.request, 'date')
        qs = apply_exact(qs, self.request, 'category')
        qs = apply_icontains(qs, self.request, 'supplier')
        return qs.order_by('-date')

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