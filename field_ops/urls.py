from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BlockActivityLogViewSet, SurveillanceReportViewSet

router = DefaultRouter()
router.register(r'block-activities', BlockActivityLogViewSet, basename='block-activity')
router.register(r'surveillance', SurveillanceReportViewSet, basename='surveillance-report')

urlpatterns = [
    path('', include(router.urls)),
]
