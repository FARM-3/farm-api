from django.contrib import admin
from .models import LookupOption, FertilizerType, FertilizerSubType, CoffeeType, CoffeeSubType


class FertilizerSubTypeInline(admin.TabularInline):
    model = FertilizerSubType
    extra = 1


@admin.register(FertilizerType)
class FertilizerTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order', 'is_active')
    inlines = [FertilizerSubTypeInline]


class CoffeeSubTypeInline(admin.TabularInline):
    model = CoffeeSubType
    extra = 1


@admin.register(CoffeeType)
class CoffeeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order', 'is_active')
    inlines = [CoffeeSubTypeInline]


@admin.register(LookupOption)
class LookupOptionAdmin(admin.ModelAdmin):
    list_display = ('category', 'value', 'label', 'default_rate', 'unit_label', 'sort_order', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('value', 'label')
