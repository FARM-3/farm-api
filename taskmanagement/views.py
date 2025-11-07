from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from .models import Season, Task, TaskComment
from .serializers import (
    SeasonSerializer, TaskSerializer, TaskCreateSerializer,
    TaskUpdateSerializer, TaskCommentSerializer,
    TaskListSerializer, BlockChampionSerializer
)

User = get_user_model()


class IsManagerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow Farm Managers to create/edit.
    Block Champions can only read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'manager'


class SeasonViewSet(viewsets.ModelViewSet):
    """
    API endpoint for seasonal calendars.
    Only Farm Managers can create/edit seasons.
    Block Champions can view seasons.
    """
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
    permission_classes = [IsManagerOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Get all tasks for a specific season"""
        season = self.get_object()
        tasks = season.tasks.all()
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get currently active seasons"""
        today = timezone.now().date()
        seasons = Season.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        )
        serializer = self.get_serializer(seasons, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming seasons"""
        today = timezone.now().date()
        seasons = Season.objects.filter(start_date__gt=today)[:5]
        serializer = self.get_serializer(seasons, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for tasks.
    Farm Managers can create and assign tasks.
    Block Champions can view their assigned tasks and update status.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.select_related(
            'assigned_to', 'created_by', 'season', 'block'
        ).prefetch_related('comments')
        
        # Block Champions only see their own tasks
        if user.role == 'block_champion':
            queryset = queryset.filter(assigned_to=user)
        
        # Apply filters from query params
        status_filter = self.request.query_params.get('status')
        priority_filter = self.request.query_params.get('priority')
        due_date = self.request.query_params.get('due_date')
        block_name = self.request.query_params.get('block_name')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        if due_date:
            queryset = queryset.filter(due_date=due_date)
        if block_name:
            queryset = queryset.filter(block_name__icontains=block_name)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        elif self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            # Block Champions use simpler update serializer
            if self.request.user.role == 'block_champion':
                return TaskUpdateSerializer
            return TaskCreateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        # Only Farm Managers can create tasks
        if self.request.user.role != 'manager':
            raise permissions.PermissionDenied(
                "Only Farm Managers can create tasks"
            )
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get all tasks assigned to the current Block Champion"""
        if request.user.role != 'block_champion':
            return Response(
                {'error': 'This endpoint is for Block Champions only'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        tasks = Task.objects.filter(assigned_to=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get tasks due today"""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            due_date=today
        ).exclude(status='COMPLETED')
        serializer = TaskListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming tasks (next 7 days)"""
        today = timezone.now().date()
        end_date = today + timezone.timedelta(days=7)
        queryset = self.get_queryset().filter(
            due_date__range=[today, end_date]
        ).exclude(status='COMPLETED')
        serializer = TaskListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue tasks"""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            due_date__lt=today
        ).exclude(status='COMPLETED')
        serializer = TaskListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Block Champion can update their task status.
        POST /api/tasks/tasks/{id}/update_status/
        Body: {"status": "IN_PROGRESS"}
        """
        task = self.get_object()
        
        # Check permission - only assigned Block Champion can update
        if request.user.role == 'block_champion' and task.assigned_to != request.user:
            return Response(
                {'error': 'You can only update tasks assigned to you'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        allowed_statuses = ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']
        
        if new_status not in allowed_statuses:
            return Response(
                {'error': f'Invalid status. Must be one of: {", ".join(allowed_statuses)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = new_status
        task.save()
        
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """
        Add a comment to a task.
        POST /api/tasks/tasks/{id}/add_comment/
        Body: {"comment": "Started working on this"}
        """
        task = self.get_object()
        comment_text = request.data.get('comment')
        
        if not comment_text:
            return Response(
                {'error': 'Comment text is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comment = TaskComment.objects.create(
            task=task,
            user=request.user,
            comment=comment_text
        )
        
        serializer = TaskCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get task statistics.
        For Block Champions: their own stats
        For Farm Managers: overall stats
        """
        user = request.user
        today = timezone.now().date()
        
        if user.role == 'block_champion':
            # Block Champion's personal stats
            base_query = Task.objects.filter(assigned_to=user)
        else:
            # Farm Manager sees all stats
            base_query = Task.objects.all()
        
        stats = {
            'total_tasks': base_query.count(),
            'pending': base_query.filter(status='PENDING').count(),
            'in_progress': base_query.filter(status='IN_PROGRESS').count(),
            'completed': base_query.filter(status='COMPLETED').count(),
            'overdue': base_query.filter(
                due_date__lt=today,
                status__in=['PENDING', 'IN_PROGRESS']
            ).count(),
            'due_today': base_query.filter(
                due_date=today,
                status__in=['PENDING', 'IN_PROGRESS']
            ).count(),
            'due_this_week': base_query.filter(
                due_date__range=[today, today + timezone.timedelta(days=7)],
                status__in=['PENDING', 'IN_PROGRESS']
            ).count(),
        }
        
        # Add breakdown by priority
        stats['by_priority'] = {
            'urgent': base_query.filter(priority='URGENT', status__in=['PENDING', 'IN_PROGRESS']).count(),
            'high': base_query.filter(priority='HIGH', status__in=['PENDING', 'IN_PROGRESS']).count(),
            'medium': base_query.filter(priority='MEDIUM', status__in=['PENDING', 'IN_PROGRESS']).count(),
            'low': base_query.filter(priority='LOW', status__in=['PENDING', 'IN_PROGRESS']).count(),
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def block_champions(self, request):
        """
        Get list of all Block Champions (for Farm Manager to assign tasks).
        Only accessible by Farm Managers.
        """
        if request.user.role != 'manager':
            return Response(
                {'error': 'Only Farm Managers can access this'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        champions = User.objects.filter(role='block_champion', is_active=True)
        serializer = BlockChampionSerializer(champions, many=True)
        return Response(serializer.data)