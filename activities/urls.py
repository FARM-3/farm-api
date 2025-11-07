from rest_framework.routers import DefaultRouter
from .views import ActivityViewSet
from django.urls import path, include

router = DefaultRouter()
router.register('activities', ActivityViewSet, basename='activities')

urlpatterns = [path('', include(router.urls))]