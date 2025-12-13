from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.
User = settings.AUTH_USER_MODEL

class Season(models.Model):
    name = models.CharField(max_length=100)
    season_type = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_seasons',
        limit_choices_to={'role': 'manager'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Season"
        verbose_name_plural = "Seasons"

    def __str__(self):
        return f"{self.name} ({self.get_season_type_display()})"
    
    @property
    def is_active(self):
        """Check if season is currently active"""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date
    
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Activity - stored as JSON array to support multiple activities
    activity = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of activity types"
    )
    custom_activity = models.CharField(
        max_length=200,
        blank=True,
        help_text="Custom activity text when 'other' is selected"
    )

    priority = models.CharField(
        max_length=50,
        blank=True,
        default='medium'
    )

    # Multiple staff assignment - stored as JSON array
    assigned_to = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of staff IDs assigned to this task"
    )

    # Creator - Can be Farm Manager (assigning) or Block Champion (self-created)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        null=True,
        blank=True,
        help_text="Farm Manager or Block Champion who created the task"
    )

    # Date and time fields
    date = models.DateField(
        default=timezone.now,
        help_text="Date when task is scheduled"
    )
    time = models.CharField(
        max_length=50,
        blank=True,
        help_text="Time of day (e.g., '2:30 PM')"
    )

    # Completion tracking
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Block assignment
    block = models.ForeignKey(
        'production.Block',
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True,
        help_text="Farm block where this task is to be performed"
    )

    # Optional season linkage
    season = models.ForeignKey(
        Season,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        help_text="Link task to a seasonal calendar"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        indexes = [
            models.Index(fields=['date', 'completed']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.date}"

    def save(self, *args, **kwargs):
        # Auto-set completed_at when completed is True
        if self.completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.completed and self.completed_at:
            # Reset completed_at if task is marked as incomplete
            self.completed_at = None
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.completed:
            return False
        return self.date < timezone.now().date()

    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if self.completed:
            return None
        delta = self.date - timezone.now().date()
        return delta.days

class TaskComment(models.Model):
    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Task Comment"
        verbose_name_plural = "Task Comments"
    
    def __str__(self):
        return f"Comment by {self.user.phone} on {self.task.title}"