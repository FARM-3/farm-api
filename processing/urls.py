from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FermentingViewSet
)

# Create a router - this automatically generates URLs for our ViewSets
router = DefaultRouter()

# Register ViewSets with the router
# The first argument is the URL prefix
# The second is the ViewSet class
router.register(r'fermenting', FermentingViewSet, basename='fermenting')

urlpatterns = [
    path('', include(router.urls)),
]
