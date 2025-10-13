from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HarvestsViewSet
from .views import BlockViewSet


router = DefaultRouter()
router.register(r'harvests', HarvestsViewSet)
router.register(r'blocks', BlockViewSet, basename='block')


urlpatterns = [
    path('', include(router.urls)),
]


