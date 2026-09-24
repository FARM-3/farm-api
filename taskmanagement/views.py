from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Season, Task, TaskComment, TaskSubmission
from .serializers import (
    SeasonSerializer, TaskSerializer, TaskCreateUpdateSerializer,
    TaskCommentSerializer, TaskListSerializer, TaskSubmissionSerializer
)

User = get_user_model()


def _task_assigned_to_staff(task, staff_id):
    """True if staff_id appears in the task assigned_to JSON array."""
    if not staff_id:
        return False
    assigned = task.assigned_to or []
    target = str(staff_id).strip()
    return any(str(entry).strip() == target for entry in assigned)


def _resolve_staff_id_for_user(user):
    """
    Resolve Staff.staff_id for a mobile user.
    Tasks are assigned by staff_id (RF001), so the user must map to a Staff row.
    Auto-links user.staff when a unique name match is found.
    """
    from financialmanagement.models import Staff

    if getattr(user, 'staff_id', None) and user.staff:
        return user.staff.staff_id

    staff = None
    name = (user.name or '').strip()
    if name:
        parts = name.split()
        if len(parts) >= 2:
            staff = Staff.objects.filter(
                first_name__iexact=parts[0],
                last_name__iexact=parts[-1],
                is_active=True,
            ).first()
        if not staff and len(parts) == 1:
            staff = Staff.objects.filter(
                first_name__iexact=parts[0],
                is_active=True,
            ).first()
        if not staff:
            name_lower = name.lower()
            for candidate in Staff.objects.filter(is_active=True):
                full = candidate.get_full_name().lower()
                if name_lower in full or full in name_lower:
                    staff = candidate
                    break

    if staff:
        if not user.staff_id:
            user.staff = staff
            user.save(update_fields=['staff'])
        return staff.staff_id

    return None


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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        task_ids = list(queryset.values_list('id', flat=True))
        status_map = {}
        for sub in TaskSubmission.objects.filter(
            assigned_task_id__in=task_ids
        ).order_by('assigned_task_id', '-updated_at', '-created_at'):
            if sub.assigned_task_id not in status_map:
                status_map[sub.assigned_task_id] = sub.status
        page = self.paginate_queryset(queryset)
        ctx = {**self.get_serializer_context(), 'submission_status_map': status_map}
        if page is not None:
            serializer = TaskListSerializer(page, many=True, context=ctx)
            return self.get_paginated_response(serializer.data)
        serializer = TaskListSerializer(queryset, many=True, context=ctx)
        return Response(serializer.data)

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


class TaskSubmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for mobile app task submissions.
    Handles both assigned tasks and self-created tasks.
    
    Endpoints:
    - GET /api/task-submissions/ - List all submissions for current user
    - GET /api/task-submissions/my-assigned-tasks/ - Get tasks assigned to me
    - POST /api/task-submissions/ - Create submission (with photo upload)
    - PATCH /api/task-submissions/{id}/ - Update submission status
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSubmissionSerializer

    def get_queryset(self):
        # Superadmins and managers can see all submissions
        # Regular users only see their own submissions
        if self.request.user.role in ['superadmin', 'manager', 'admin']:
            queryset = TaskSubmission.objects.all()
        else:
            queryset = TaskSubmission.objects.filter(user=self.request.user)

        # Optional filters
        status_filter = self.request.query_params.get('status')
        assigned_task_filter = self.request.query_params.get('assigned_task_id')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if assigned_task_filter:
            queryset = queryset.filter(assigned_task_id=assigned_task_filter)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        # Automatically set the user to the logged-in user
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_assigned_tasks(self, request):
        """
        Get all tasks assigned to the current user from the Task model.
        Matches by linked Staff.staff_id (auto-linked from user name when possible).
        """
        user = request.user
        staff_reference = _resolve_staff_id_for_user(user)

        if not staff_reference:
            return Response([])

        candidates = Task.objects.filter(completed=False).select_related('created_by', 'block')
        assigned_tasks = [t for t in candidates if _task_assigned_to_staff(t, staff_reference)]

        tasks_with_submission_status = []
        for task in assigned_tasks:
            task_data = TaskSerializer(task).data
            task_data['is_assigned'] = True

            try:
                submission = TaskSubmission.objects.filter(
                    assigned_task_id=task.id,
                    user=request.user
                ).order_by('-updated_at', '-created_at').first()
                task_data['has_submission'] = submission is not None
                task_data['submission_status'] = submission.status if submission else 'assigned'
            except Exception:
                task_data['has_submission'] = False
                task_data['submission_status'] = 'assigned'

            tasks_with_submission_status.append(task_data)

        return Response(tasks_with_submission_status)

    @action(detail=False, methods=['get'])
    def my_submissions(self, request):
        """
        Get all task submissions by the current user.
        Includes both assigned tasks and self-created tasks.
        """
        submissions = self.get_queryset()
        serializer = self.get_serializer(submissions, many=True)
        return Response(serializer.data)
