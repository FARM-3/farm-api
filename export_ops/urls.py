from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WarehouseViewSet, InventoryLotViewSet,
    DispatchNoteViewSet, ExportTraceRecordViewSet,
)

router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'inventory', InventoryLotViewSet, basename='inventory-lot')
router.register(r'dispatch', DispatchNoteViewSet, basename='dispatch-note')
router.register(r'trace-records', ExportTraceRecordViewSet, basename='export-trace')

urlpatterns = [
    path('', include(router.urls)),
]
