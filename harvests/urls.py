from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HarvestsViewSet

router = DefaultRouter()
router.register(r'harvests', HarvestsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
