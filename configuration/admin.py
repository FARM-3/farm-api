from django.contrib import admin
from .models import LookupOption


@admin.register(LookupOption)
class LookupOptionAdmin(admin.ModelAdmin):
    list_display = ('category', 'value', 'label', 'sort_order', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('value', 'label')
