from django.shortcuts import render
from rest_framework import viewsets
from .models import Wage
from .serializers import WageSerializer, SaleSerializer, ExpenseSerializer
from .models import Sale, Expense
from rest_framework.permissions import AllowAny

# Create your views here.
class WageViewSet(viewsets.ModelViewSet):
    queryset = Wage.objects.all()
    serializer_class = WageSerializer

class SaleViewSet(viewsets.ModelViewSet):
    
    queryset = Sale.objects.all().order_by('-date_of_payment', 'customer_name')
    serializer_class = SaleSerializer
    permission_classes = [AllowAny] 

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

