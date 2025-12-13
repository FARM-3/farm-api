from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Season, Task, TaskComment

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for custom User model"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone', 'name', 'role', 'role_display']
        read_only_fields = ['id', 'phone', 'role']


class SeasonSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    task_count = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Season
        fields = [
            'id', 'name', 'season_type', 'start_date', 'end_date',
            'description', 'created_by', 'task_count', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_task_count(self, obj):
        return obj.tasks.count()


class TaskCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'user', 'user_name', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    """Main serializer for Task with all fields"""
    created_by = UserSerializer(read_only=True)
    season_name = serializers.CharField(source='season.name', read_only=True)
    block_name = serializers.CharField(source='block.name', read_only=True, allow_null=True)
    block_id = serializers.IntegerField(source='block.block_id', read_only=True, allow_null=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_until_due = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'activity', 'custom_activity',
            'priority', 'assigned_to', 'created_by', 'date', 'time',
            'completed', 'completed_at', 'season', 'season_name',
            'block', 'block_name', 'block_id', 'comments',
            'is_overdue', 'days_until_due', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'completed_at', 'created_at', 'updated_at']


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating tasks - no validation"""

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'activity', 'custom_activity',
            'priority', 'assigned_to', 'date', 'time',
            'completed', 'season', 'block'
        ]


class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for task lists"""
    block_name = serializers.CharField(source='block.name', read_only=True, allow_null=True)
    block_id = serializers.IntegerField(source='block.block_id', read_only=True, allow_null=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'priority', 'assigned_to',
            'date', 'time', 'completed', 'is_overdue',
            'block', 'block_name', 'block_id', 'activity',
            'created_at'
        ]
