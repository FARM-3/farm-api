from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FarmerViewSet, FarmerHarvestViewSet

router = DefaultRouter()
router.register(r'farmer', FarmerViewSet)
router.register(r'farmer-harvest', FarmerHarvestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
]
