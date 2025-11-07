from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import ViewSets here when they are created
# from .views import HarvestViewSet, BlockViewSet

router = DefaultRouter()
# router.register(r'harvests', HarvestViewSet)
# router.register(r'blocks', BlockViewSet)

urlpatterns = [
    path('', include(router.urls)),
]  