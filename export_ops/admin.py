from django.contrib import admin
from .models import Warehouse, InventoryLot, DispatchNote, ExportTraceRecord

admin.site.register(Warehouse)
admin.site.register(InventoryLot)
admin.site.register(DispatchNote)
admin.site.register(ExportTraceRecord)
