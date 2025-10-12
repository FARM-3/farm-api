from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FarmerViewSet, FarmerHarvestViewSet, get_wakiso_parishes

router = DefaultRouter()
router.register(r'FarmerRegistration', FarmerViewSet)
router.register(r'FarmerHarvest', FarmerHarvestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('wakiso-parishes/', get_wakiso_parishes, name='wakiso-parishes'),
]
