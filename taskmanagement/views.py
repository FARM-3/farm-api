from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Season, Task, TaskComment
from .serializers import (
    SeasonSerializer, TaskSerializer, TaskCreateUpdateSerializer,
    TaskCommentSerializer, TaskListSerializer
)

User = get_user_model()


class SeasonViewSet(viewsets.ModelViewSet):
    """
    API endpoint for seasonal calendars.
    """
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    API endpoint for tasks - matches frontend TaskCalendarScreen structure.
    No role-based restrictions, minimal validation.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Task.objects.select_related(
            'created_by', 'season', 'block'
        ).prefetch_related('comments')

        # Apply filters from query params
        date_filter = self.request.query_params.get('date')
        priority_filter = self.request.query_params.get('priority')
        completed_filter = self.request.query_params.get('completed')
        block_filter = self.request.query_params.get('block')

        if date_filter:
            queryset = queryset.filter(date=date_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        if completed_filter is not None:
            completed_bool = completed_filter.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(completed=completed_bool)
        if block_filter:
            queryset = queryset.filter(block_id=block_filter)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TaskCreateUpdateSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get tasks for today"""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(date=today)
        serializer = TaskListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming tasks (next 7 days)"""
        today = timezone.now().date()
        end_date = today + timezone.timedelta(days=7)
        queryset = self.get_queryset().filter(
            date__range=[today, end_date]
        ).filter(completed=False)
        serializer = TaskListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue incomplete tasks"""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            date__lt=today,
            completed=False
        )
        serializer = TaskListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'patch'])
    def toggle_complete(self, request, pk=None):
        """
        Toggle task completion status.
        POST/PATCH /api/tasks/{id}/toggle_complete/
        """
        task = self.get_object()
        task.completed = not task.completed
        task.save()

        serializer = TaskSerializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """
        Add a comment to a task.
        POST /api/tasks/{id}/add_comment/
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
        """
        today = timezone.now().date()
        base_query = self.get_queryset()

        stats = {
            'total_tasks': base_query.count(),
            'completed': base_query.filter(completed=True).count(),
            'pending': base_query.filter(completed=False).count(),
            'overdue': base_query.filter(
                date__lt=today,
                completed=False
            ).count(),
            'due_today': base_query.filter(
                date=today,
                completed=False
            ).count(),
            'due_this_week': base_query.filter(
                date__range=[today, today + timezone.timedelta(days=7)],
                completed=False
            ).count(),
        }

        # Add breakdown by priority (only incomplete tasks)
        incomplete_tasks = base_query.filter(completed=False)
        stats['by_priority'] = {
            'high': incomplete_tasks.filter(priority='high').count(),
            'medium': incomplete_tasks.filter(priority='medium').count(),
            'low': incomplete_tasks.filter(priority='low').count(),
        }

        return Response(stats)
