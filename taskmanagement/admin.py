from django.contrib import admin
from .models import Season, Task, TaskComment, TaskSubmission


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


@admin.register(TaskSubmission)
class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'assigned_task_id', 'status', 'activity', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'user__phone', 'user__name', 'assigned_task_id']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Task Information', {
            'fields': ('assigned_task_id', 'user', 'title', 'description', 'activity', 'priority', 'block_id')
        }),
        ('Status & Timestamps', {
            'fields': ('status', 'accepted_at', 'rejected_at', 'started_at', 'completed_at', 'duration_minutes')
        }),
        ('Evidence & Comments', {
            'fields': ('photos', 'completion_comment', 'metadata')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at')
        }),
    )
