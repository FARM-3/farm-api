from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaleViewSet, WageViewSet, ExpenseViewSet

router = DefaultRouter()
router.register(r'wages', WageViewSet)
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    path('', include(router.urls)),
]
