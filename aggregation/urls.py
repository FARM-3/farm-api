from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FarmerRegistrationViewSet, FarmerHarvestViewSet

router = DefaultRouter()
router.register(r'Farmer', FarmerRegistrationViewSet)
router.register(r'FarmerHarvest', FarmerHarvestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
]
