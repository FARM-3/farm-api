from django.conf import settings
from django.db import models


class BlockActivityLog(models.Model):
    """EzyAgric-style crop production log — practices & inputs per block."""

    LOG_TYPES = [
        ('practice', 'Farm Practice'),
        ('input', 'Input Application'),
        ('scouting', 'Scouting'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ]
    INPUT_TYPES = [
        ('fertilizer', 'Fertilizer'),
        ('pesticide', 'Pesticide'),
        ('organic', 'Organic Input'),
        ('other', 'Other'),
    ]

    log_id = models.CharField(max_length=30, unique=True)
    block_id = models.CharField(max_length=50, db_index=True)
    log_type = models.CharField(max_length=20, choices=LOG_TYPES, default='practice')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    practices = models.JSONField(default=list, blank=True, help_text='Standard practices applied')
    input_type = models.CharField(max_length=20, choices=INPUT_TYPES, blank=True)
    input_name = models.CharField(max_length=200, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=30, blank=True, help_text='kg, L, bags, etc.')
    activity_date = models.DateField()
    weather_conditions = models.JSONField(default=list, blank=True)
    gps_coordinates = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='field_ops/activities/%Y/%m/', blank=True, null=True)
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='block_activity_logs',
    )
    reported_by_name = models.CharField(max_length=200, blank=True)
    harvest_id = models.CharField(max_length=100, blank=True, help_text='Optional link to harvest lot')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-activity_date', '-created_at']
        verbose_name = 'Block Activity Log'
        verbose_name_plural = 'Block Activity Logs'

    def __str__(self):
        return f'{self.block_id} — {self.title} ({self.activity_date})'


class SurveillanceReport(models.Model):
    """Field surveillance / exception reports from mobile — shown on web Task Management."""

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_review', 'In Review'),
        ('resolved', 'Resolved'),
    ]
    ISSUE_TYPES = [
        ('pest', 'Pest Infestation'),
        ('disease', 'Disease'),
        ('drought', 'Drought / Water Stress'),
        ('theft', 'Theft / Damage'),
        ('compliance', 'Compliance Issue'),
        ('quality', 'Cherry Quality'),
        ('other', 'Other'),
    ]

    report_id = models.CharField(max_length=30, unique=True)
    block_id = models.CharField(max_length=50, blank=True, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPES, default='other')
    weather_conditions = models.JSONField(default=list, blank=True)
    location = models.CharField(max_length=200, blank=True)
    gps_coordinates = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='field_ops/surveillance/%Y/%m/', blank=True, null=True)
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='surveillance_reports',
    )
    reported_by_name = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Surveillance Report'
        verbose_name_plural = 'Surveillance Reports'

    def __str__(self):
        return f'{self.report_id} — {self.title}'
