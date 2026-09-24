from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LookupOptionViewSet, CoffeeTypeViewSet, FertilizerTypeViewSet,
    FarmAssetViewSet, FarmDocumentViewSet, TrainingRecordViewSet,
)

router = DefaultRouter()
router.register(r'lookups', LookupOptionViewSet, basename='lookup-option')
router.register(r'coffee-types', CoffeeTypeViewSet, basename='coffee-type')
router.register(r'fertilizer-types', FertilizerTypeViewSet, basename='fertilizer-type')
router.register(r'assets', FarmAssetViewSet, basename='farm-asset')
router.register(r'documents', FarmDocumentViewSet, basename='farm-document')
router.register(r'trainings', TrainingRecordViewSet, basename='training-record')

urlpatterns = [
    path('', include(router.urls)),
]
