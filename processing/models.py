
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

class Bagging(models.Model):
    """
    Final stage: Bagging process
    Tracks coffee batches during final packaging
    """
    processing_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique ID for this bagging batch (e.g., BAG-2024-001)"
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
    
    moisture_content = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Final moisture content percentage (0-100%)"
    )
    
    date = models.DateField(
        help_text="Date when bagging occurred"
    )
    
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Final weight in kg"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Bagging Process"
        verbose_name_plural = "Bagging Processes"
    
    def __str__(self):
        return f"{self.processing_id} - {self.name}"
