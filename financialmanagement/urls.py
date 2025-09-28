from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WageViewSet

router = DefaultRouter()
router.register(r'wages', WageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
