from django.shortcuts import render
from rest_framework import viewsets
from .models import Balancesheet, Wage
from .serializers import WageSerializer, SaleSerializer, ExpenseSerializer, BalancesheetSerializer
from .models import Sale, Expense   
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from datetime import datetime

# Create your views here.
class WageViewSet(viewsets.ModelViewSet):
    queryset = Wage.objects.all()
    serializer_class = WageSerializer

class SaleViewSet(viewsets.ModelViewSet):

    queryset = Sale.objects.all().order_by('-date_of_payment', 'first_name')
    serializer_class = SaleSerializer
    permission_classes = [AllowAny]

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

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

        

