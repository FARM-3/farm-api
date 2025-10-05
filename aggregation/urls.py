from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FarmerViewSet
from .views import FarmerHarvestViewSet

router = DefaultRouter()
router.register(r'Farmer', FarmerViewSet)
router.register(r'FarmerHarvest', FarmerHarvestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
