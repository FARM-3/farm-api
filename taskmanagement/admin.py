from django.contrib import admin
from .models import Season, Task, TaskComment


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['name', 'season_type', 'start_date', 'end_date', 'created_by', 'is_active']
    list_filter = ['season_type', 'start_date']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'date', 'completed', 'is_overdue', 'created_by']
    list_filter = ['priority', 'date', 'completed', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['completed_at', 'created_at', 'updated_at']
    raw_id_fields = ['created_by', 'season', 'block']


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'created_at']
    search_fields = ['comment', 'user__phone']
    readonly_fields = ['created_at']
