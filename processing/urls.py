from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FermentingViewSet,
    WashingViewSet,
    NaturalSundryingViewSet,
    DryingViewSet,
    BaggingViewSet,
    RipenessViewSet,
    FloatingViewSet
)

# Create a router - this automatically generates URLs for our ViewSets
router = DefaultRouter()

# Register ViewSets with the router
# The first argument is the URL prefix
# The second is the ViewSet class
router.register(r'fermenting', FermentingViewSet, basename='fermenting')
router.register(r'washing', WashingViewSet, basename='washing')
router.register(r'sundrying', NaturalSundryingViewSet, basename='sundrying')
router.register(r'drying', DryingViewSet, basename='drying')
router.register(r'bagging', BaggingViewSet, basename='bagging')
router.register(r'ripeness', RipenessViewSet, basename='ripeness')
router.register(r'floating', FloatingViewSet, basename='floating')



urlpatterns = [
    path('', include(router.urls)),
]
