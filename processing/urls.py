from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FermentingViewSet,
    WashingViewSet,
    NaturalSundryingViewSet,
    DryingViewSet,
    HullingViewSet,
    BaggingViewSet,
    RipenessViewSet,
    FloatingViewSet,
    BatchViewSet
)
from .trace_views import HarvestTrackView, TraceScanView

# Create a router - this automatically generates URLs for our ViewSets
router = DefaultRouter()

# Register ViewSets with the router
# The first argument is the URL prefix
# The second is the ViewSet class
router.register(r'fermenting', FermentingViewSet, basename='fermenting')
router.register(r'washing', WashingViewSet, basename='washing')
router.register(r'sundrying', NaturalSundryingViewSet, basename='sundrying')
router.register(r'drying', DryingViewSet, basename='drying')
router.register(r'hulling', HullingViewSet, basename='hulling')
router.register(r'bagging', BaggingViewSet, basename='bagging')
router.register(r'ripeness', RipenessViewSet, basename='ripeness')
router.register(r'floating', FloatingViewSet, basename='floating')
router.register(r'batch', BatchViewSet, basename='batch')



urlpatterns = [
    path('track/<str:harvest_id>/', HarvestTrackView.as_view(), name='harvest-track'),
    path('trace/scan/', TraceScanView.as_view(), name='trace-scan'),
    path('', include(router.urls)),
]
