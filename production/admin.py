from django.contrib import admin
from .models import Block

# Register your models here.
@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ['block_id', 'type_of_coffee', 'no_of_trees', 'date_planted', 'created_at']
    list_filter = ['use_pesticides', 'created_at']
    search_fields = ['block_id', 'type_of_coffee']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('block_id', 'no_of_trees', 'date_planted')
        }),
        ('Coffee Details', {
            'fields': ('type_of_coffee',)
        }),
        ('Seedling Information', {
            'fields': ('source_of_seedling', 'type_of_seedling', 'age_of_seedling')
        }),
        ('Farm Practices', {
            'fields': ('use_pesticides', 'pesticides_list', 'standard_practices')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )