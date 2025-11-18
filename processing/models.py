
# Create your models here.

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone




# Choice tuples for dropdown options
GRADE_CHOICES = [
    ('A', 'Grade A'),
    ('B', 'Grade B'),
    ('C', 'Grade C'),
]

WEATHER_CHOICES = [
    ('sunny', 'Sunny'),
    ('raining', 'Raining'),
    ('cloudy', 'Cloudy'),
]


class Fermenting(models.Model):
    """
    First stage: Fermenting process
    Tracks coffee batches during fermentation
    """
    # Processing ID - auto-generated unique identifier
    processing_id = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Unique ID for this fermentation batch (e.g., FERM-2024-001)"
    )
    
    # Duration in days
    days = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of days for fermentation"
    )
    
    # Batch name
    name = models.CharField(
        max_length=100,
        help_text="Descriptive name for this batch"
    )
    
    # Coffee grade
    grade = models.CharField(
        max_length=1,
        choices=GRADE_CHOICES,
        help_text="Quality grade of the coffee"
    )
    CHERRY_COLOUR_CHOICES = [
        ('red', 'Red'),
        ('green', 'Green'),
        ('Yellow', 'yellow'),
        ('Black', 'Black'),
    ]
    cherry_colour = models.CharField(
        max_length=10,
        choices=CHERRY_COLOUR_CHOICES,
        help_text="Cherry colour",
        null=True, # Allow nulls for migration
        blank=True,

    )
    
    # Processing date
    date = models.DateField(default=timezone.now)
    
    # Weight tracking
    weight_before = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Weight in kg before fermentation"
    )
    
    weight_after = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Weight in kg after fermentation"
    )
    
    # Metadata fields (automatic timestamps)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']  # Most recent first
        verbose_name = "Fermenting Process"
        verbose_name_plural = "Fermenting Processes"
    
    def __str__(self):
        return f"{self.processing_id} - {self.name}"
    
    @property
    def weight_loss(self) -> float: #Add type hint
        """Calculate weight loss during fermentation"""
        return self.weight_before - self.weight_after

class Washing(models.Model):
    """
    Second stage: Washing process
    Tracks coffee batches during washing
    """
    processing_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated: WASH-{DDMMYY}-{SEQ}"

    )
       
    
    name = models.CharField(
        max_length=100,
        help_text="Descriptive name for this batch"
    )
    
    grade = models.CharField(
        max_length=1,
        choices=GRADE_CHOICES,
        help_text="Quality grade of the coffee"
    )
    CHERRY_COLOUR_CHOICES = [
        ('red', 'Red'),
        ('green', 'Green'),
        ('Yellow', 'Yellow'),
        ('Black', 'Black'),
    ]
    cherry_colour = models.CharField(
        max_length=10,
        choices=CHERRY_COLOUR_CHOICES,
        help_text="Cherry colour",
        null=True, #Allow nulls for migration
        blank=True,

    )

    
    date = models.DateField(default=timezone.now)
    
    weight_before = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Weight in kg before washing"
    )
    
    weight_after = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Weight in kg after washing"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Washing Process"
        verbose_name_plural = "Washing Processes"
    
    def __str__(self):
        return f"{self.processing_id} - {self.name}"
    
    @property
    def weight_loss(self) -> float: #Add type hint
        """Calculate weight loss during washing"""
        return self.weight_before - self.weight_after
    
class Sundrying(models.Model):
     """
    Third stage: Sundrying process
    Tracks coffee batches during sun drying with weather conditions
     """
     processing_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated: DRY-{DDMMYY}-{SEQ}"
    )
    
     name = models.CharField(
        max_length=100,
        help_text="Descriptive name for this batch"
    )
    
     grade = models.CharField(
        max_length=1,
        choices=GRADE_CHOICES,
        help_text="Quality grade of the coffee"
    )
     CHERRY_COLOUR_CHOICES = [
        ('red', 'Red'),
        ('green', 'Green'),
        ('Yellow', 'Yellow'),
        ('Black', 'Black'),
    ]
     cherry_colour = models.CharField(
        max_length=10,
        choices=CHERRY_COLOUR_CHOICES,
        help_text="Cherry colour",
        null=True, #Allow nulls for migration
        blank=True,
        
    )
    
    
    # Weather tracking
     weather = models.CharField(
        max_length=10,
        choices=WEATHER_CHOICES,
        help_text="Weather conditions during drying"
    )
    
     temperature = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Temperature in Celsius"
    )
    
    # Moisture content tracking
     moisture_content = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Moisture content percentage (0-100%)"
    )
    
     date = models.DateField(default=timezone.now)
    
     weight_before = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Weight in kg before drying"
    )
    
     weight_after = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Weight in kg after drying"
    )
    
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)
    
     class Meta:
        ordering = ['-date']
        verbose_name = "Sundrying Process"
        verbose_name_plural = "Sundrying Processes"
    
     def __str__(self):
        return f"{self.processing_id} - {self.name}"
    
     @property
     def weight_loss(self) -> float: #Add type hint
        """Calculate weight loss during sundrying"""
        return self.weight_before - self.weight_after


 # ...existing code...
class Bagging(models.Model):
    """
    Bagging record (attributes from brainstorm):
    - lot_id: same lot id used under drying (select existing)
    - weight: kgs
    - moisture_content: percent
    - no_of_bags: integer
    - date: bagging datetime
    - outturn / expected_outturn: auto-generated (nullable) - populated by backend or sync
    - qr_code: flexible string for now (left blank until you decide payload)
    """
    lot_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Lot id from drying (select existing drying lot_id)"
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Weight in kilograms"
    )
    moisture_content = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Moisture content percentage (0-100)"
    )
    no_of_bags = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Total number of bags"
    )
    date = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time when bagging was completed"
    )

    # Auto-generated / pulled values (nullable until computed)
    outturn = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        help_text="Measured outturn (pulled from drying or computed during sync)"
    )
    expected_outturn = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        help_text="Expected outturn (pulled from drying or computed during sync)"
    )

    # QR payload (left flexible for now)
    qr_code = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="QR code payload (which process / farmer / grade / harvest time) - leave blank until defined"
    )

    # metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Bagging Record'
        verbose_name_plural = 'Bagging Records'
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['lot_id']),
        ]

    def __str__(self):
        return f"Lot {self.lot_id} - {self.no_of_bags} bags ({self.weight}kg)"

    @property
    def average_weight_per_bag(self):
        if self.no_of_bags > 0:
            return round(self.weight / self.no_of_bags, 2)
        return 0

    def clean(self):
        if self.moisture_content < 0 or self.moisture_content > 100:
            raise ValidationError({'moisture_content': 'Moisture must be 0-100 percent'})
        if self.weight <= 0:
            raise ValidationError({'weight': 'Weight must be > 0'})
        if self.no_of_bags <= 0:
            raise ValidationError({'no_of_bags': 'Number of bags must be at least 1'})

    def save(self, *args, **kwargs):
        # outturn / expected_outturn: leave null here.
        # If you want server-side generation, implement logic here to pull drying data
        # via lot_id (or link to Sundrying model) and set outturn/expected_outturn before save.
        self.full_clean()
        super().save(*args, **kwargs)
# ...existing code...       