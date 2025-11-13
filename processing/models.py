
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
    Final stage in coffee processing - records bagging details for traceability
    """
    lot_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique identifier for the coffee lot"
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Total weight in kilograms"
    )
    moisture = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MinValueValidator(100)],
        help_text="Moisture content percentage"
    )
    number_of_bags = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Total number of bags"
    )
    bagging_date = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time when bagging was completed"
    )
    bagged_by = models.CharField(
        max_length=200,
        help_text="Name of the person/team who performed bagging"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes or observations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-bagging_date']
        verbose_name = 'Bagging Record'
        verbose_name_plural = 'Bagging Records'
        indexes = [
            models.Index(fields=['-bagging_date']),
            models.Index(fields=['lot_id']),
        ]

    def __str__(self):
        return f"Lot {self.lot_id} - {self.number_of_bags} bags ({self.weight}kg)"

    @property
    def average_weight_per_bag(self):
        """Calculate average weight per bag"""
        if self.number_of_bags > 0:
            return round(self.weight / self.number_of_bags, 2)
        return 0

    def clean(self):
        """Validate data before saving"""
        from django.core.exceptions import ValidationError
        
        if self.moisture < 0 or self.moisture > 100:
            raise ValidationError({
                'moisture': 'Moisture content must be between 0 and 100 percent'
            })
        
        if self.weight <= 0:
            raise ValidationError({
                'weight': 'Weight must be greater than 0'
            })
        
        if self.number_of_bags <= 0:
            raise ValidationError({
                'number_of_bags': 'Number of bags must be at least 1'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)