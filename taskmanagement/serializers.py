from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Season, Task, TaskComment, TaskSubmission

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


class TaskSubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer for TaskSubmission - mobile app task submissions.
    No validation - accepts all CharField/JSONField data from frontend.
    Handles photo file uploads during sync.
    """
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    
    # Photo upload field (accepts multiple files during sync)
    uploaded_photos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        help_text="Upload photo files during sync"
    )

    class Meta:
        model = TaskSubmission
        fields = [
            'id', 'assigned_task_id', 'user', 'user_name', 'user_phone',
            'title', 'description', 'activity', 'priority', 'block_id',
            'status', 'accepted_at', 'rejected_at', 'started_at', 'completed_at',
            'duration_minutes', 'photos', 'uploaded_photos', 'completion_comment',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Handle photo uploads
        uploaded_photos = validated_data.pop('uploaded_photos', [])
        
        # Create the submission
        submission = TaskSubmission.objects.create(**validated_data)
        
        # Save photos and store URLs
        photo_urls = []
        for idx, photo_file in enumerate(uploaded_photos):
            # Save photo with unique filename
            import uuid
            from django.core.files.storage import default_storage
            filename = f"task_photos/{submission.id}_{uuid.uuid4().hex[:8]}_{photo_file.name}"
            path = default_storage.save(filename, photo_file)
            photo_urls.append(f"/media/{path}")
        
        # Update photos field with URLs
        if photo_urls:
            submission.photos = photo_urls
            submission.save()
        
        return submission

    def update(self, instance, validated_data):
        # Handle photo uploads for updates
        uploaded_photos = validated_data.pop('uploaded_photos', [])
        
        # Update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Add new photos to existing ones
        if uploaded_photos:
            import uuid
            from django.core.files.storage import default_storage
            new_photo_urls = []
            for idx, photo_file in enumerate(uploaded_photos):
                filename = f"task_photos/{instance.id}_{uuid.uuid4().hex[:8]}_{photo_file.name}"
                path = default_storage.save(filename, photo_file)
                new_photo_urls.append(f"/media/{path}")
            
            # Append to existing photos
            instance.photos = instance.photos + new_photo_urls
        
        instance.save()
        return instance
