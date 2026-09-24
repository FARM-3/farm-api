from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SaleViewSet, WageViewSet, ExpenseViewSet, BalanceSheetViewSet,
    FinancialSummaryView, StaffViewSet, SetpriceViewSet, CustomerViewSet, SupplierViewSet,
)

router = DefaultRouter()
router.register(r'staff', StaffViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'wages', WageViewSet)
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'balancesheet', BalanceSheetViewSet, basename='balance-sheet')
router.register(r'setprice', SetpriceViewSet, basename='setprice')

urlpatterns = [
    path('', include(router.urls)),
    path('financial-summary/', FinancialSummaryView.as_view(), name='financial-summary'),
]
