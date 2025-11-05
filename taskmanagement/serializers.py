from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Season, Task, TaskComment, TaskReminder

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for custom User model"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'phone', 'name', 'role', 'role_display']
        read_only_fields = ['id', 'phone', 'role']

class BlockChampionSerializer(serializers.ModelSerializer):
    """Serializer specifically for Block Champions"""
    class Meta:
        model = User
        fields = ['id', 'phone', 'name']

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
    
    def validate(self, data):
        """Ensure end_date is after start_date"""
        if data.get('start_date') and data.get('end_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError(
                    "End date must be after start date"
                )
        return data
    
class TaskCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'user', 'user_name', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    assigned_to_phone = serializers.CharField(write_only=True, required=False)
    season_name = serializers.CharField(source='season.name', read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_until_due = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'priority', 'priority_display', 'assigned_to', 'assigned_to_phone',
            'created_by', 'due_date', 'due_time', 'completed_at',
            'season', 'season_name', 'block_name', 'location', 'crop_type',
            'comments', 'attachments', 'is_overdue', 'days_until_due',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'completed_at', 'created_at', 'updated_at']

class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks"""
    assigned_to_phone = serializers.CharField(required=True)
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'status', 'priority',
            'assigned_to_phone', 'due_date', 'due_time',
            'season', 'block_name', 'location', 'crop_type'
        ]
    
    def validate_assigned_to_phone(self, value):
        """Validate that the phone belongs to a Block Champion"""
        try:
            user = User.objects.get(phone=value, role='block_champion')
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No Block Champion found with this phone number"
            )
    
    def create(self, validated_data):
        # Get the Block Champion by phone
        phone = validated_data.pop('assigned_to_phone')
        assigned_to = User.objects.get(phone=phone, role='block_champion')
        
        # Create the task
        task = Task.objects.create(
            assigned_to=assigned_to,
            **validated_data
        )
        return task
    
class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for Block Champion updating their own tasks"""
    class Meta:
        model = Task
        fields = ['status', 'description']
    
    def validate_status(self, value):
        """Only allow certain status transitions"""
        allowed_statuses = ['PENDING', 'IN_PROGRESS', 'COMPLETED']
        if value not in allowed_statuses:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(allowed_statuses)}"
            )
        return value

class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for task lists"""
    assigned_to_name = serializers.CharField(source='assigned_to.name', read_only=True)
    assigned_to_phone = serializers.CharField(source='assigned_to.phone', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'status', 'status_display',
            'priority', 'priority_display', 'assigned_to_name',
            'assigned_to_phone', 'due_date', 'is_overdue',
            'block_name', 'created_at'
        ]
