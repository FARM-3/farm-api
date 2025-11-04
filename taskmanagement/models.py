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
