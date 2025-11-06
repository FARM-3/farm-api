from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FarmerViewSet, FarmerHarvestViewSet, reverse_geocode

router = DefaultRouter()
router.register(r'farmer', FarmerViewSet)
router.register(r'farmer-harvest', FarmerHarvestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('reverse-geocode/', reverse_geocode, name='reverse-geocode'),
]
