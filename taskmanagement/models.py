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
    description = models.TextField()
    status = models.CharField(max_length=50)
    priority = models.CharField(max_length=50)
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='assigned_tasks',
        limit_choices_to={'role': 'block_champion'},
        help_text="Block Champion assigned to this task"
    )
    # Creator - Can be Farm Manager (assigning) or Block Champion (self-created)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_tasks',
        help_text="Farm Manager or Block Champion who created the task"
    )
    due_date = models.DateField()
    completed_at = models.DateTimeField(null=True, blank=True)
    season = models.ForeignKey(
        Season, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='tasks',
        help_text="Link task to a seasonal calendar"
    )

    block = models.ForeignKey(
    'production.Block',
    on_delete=models.CASCADE,
    related_name='tasks',
    help_text="Farm block where this task is to be performed"
)
    location = models.CharField(
    max_length=200, 
    blank=True,
    help_text="Specific location details within the block"
)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date', '-priority']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        indexes = [
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['due_date', 'status']),
        ]

    def __str__(self):
        return f"{self.title} - {self.assigned_to.phone} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Auto-set completed_at when status changes to COMPLETED
        if self.status == 'COMPLETED' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'COMPLETED' and self.completed_at:
            # Reset completed_at if status changes from completed
            self.completed_at = None
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.status == 'COMPLETED':
            return False
        return self.due_date < timezone.now().date()
    
    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if self.status == 'COMPLETED':
            return None
        delta = self.due_date - timezone.now().date()
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