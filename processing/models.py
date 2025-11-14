
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


class Ripeness(models.Model):
    """
    Quality Control - Ripeness Test
    First step of processing: tests the ripeness of coffee cherries
    Measures percentage of red cherries in a sample
    """
    # Foreign key to Harvests (production app)
    harvest = models.OneToOneField(
        'production.Harvests',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='ripeness_test',
        help_text="Harvest batch being tested for ripeness"
    )

    # Test date
    date = models.DateField(
        default=timezone.now,
        help_text="Date when ripeness test was performed"
    )

    # Sample size (default 100 cherries)
    sample_size = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(1)],
        help_text="Total number of cherries in sample (default: 100)"
    )

    # Number of red cherries counted
    no_of_redcherry = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        help_text="Number of red cherries found in the sample"
    )

    # Ripeness score (auto-calculated percentage)
    ripeness_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        editable=False,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Auto-calculated: (no_of_redcherry / sample_size) * 100"
    )

    # Metadata timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Ripeness Test"
        verbose_name_plural = "Ripeness Tests"

    def __str__(self):
        return f"{self.harvest.harvest_id} - Ripeness: {self.ripeness_score}%"

    def save(self, *args, **kwargs):
        """Auto-calculate ripeness_score before saving"""
        # Calculate ripeness percentage
        if self.sample_size > 0:
            self.ripeness_score = (self.no_of_redcherry / self.sample_size) * 100
        else:
            self.ripeness_score = 0

        super().save(*args, **kwargs)

    def clean(self):
        """Validate that no_of_redcherry doesn't exceed sample_size"""
        from django.core.exceptions import ValidationError
        if self.no_of_redcherry > self.sample_size:
            raise ValidationError({
                'no_of_redcherry': f'Number of red cherries ({self.no_of_redcherry}) cannot exceed sample size ({self.sample_size})'
            })


class Floating(models.Model):
    """
    Quality Control - Floating Test
    Second step: separates coffee into grades based on floating behavior
    Grade A: netweight (sinkers), Grade B: floaters
    """
    # Primary key: auto-generated grade_id (format: GRA1411A00 or GRB1010B22)
    grade_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        primary_key=True,
        help_text="Auto-generated: GR{A/B}{DDMM}{Letter}{00-99} (e.g., GRA1411A00)"
    )

    # Foreign key to Harvests (production app)
    harvest = models.ForeignKey(
        'production.Harvests',
        on_delete=models.CASCADE,
        related_name='floating_tests',
        help_text="Harvest batch being tested for floating"
    )

    # Grade (A for netweight/sinkers, B for floaters)
    # No choices - frontend will handle validation
    grade = models.CharField(
        max_length=50,
        help_text="Grade classification (e.g., A for netweight, B for floaters)"
    )

    # Weight after floating test
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Weight in kg after floating test"
    )

    # Test date
    date = models.DateField(
        default=timezone.now,
        help_text="Date when floating test was performed"
    )

    # Ripeness score (auto-filled from related Ripeness test)
    ripeness_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Auto-filled from ripeness test of same harvest"
    )

    # Metadata timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Floating Test"
        verbose_name_plural = "Floating Tests"

    def __str__(self):
        return f"{self.grade_id} - Grade {self.grade} ({self.weight}kg)"

    def save(self, *args, **kwargs):
        """
        Auto-generate grade_id and auto-fill ripeness_score before saving
        """
        # Auto-generate grade_id if not exists
        if not self.grade_id:
            self.grade_id = self.generate_grade_id()

        # Auto-fill ripeness_score from related Ripeness test
        if not self.ripeness_score:
            try:
                ripeness_test = Ripeness.objects.get(harvest=self.harvest)
                self.ripeness_score = ripeness_test.ripeness_score
            except Ripeness.DoesNotExist:
                # No ripeness test found - leave as None
                pass

        super().save(*args, **kwargs)

    def generate_grade_id(self):
        """
        Generate grade_id in format: GR{A/B}{DDMM}{Letter}{00-99}

        Examples:
            - GRA1411A00: Grade A, Nov 14 (14th day, 11th month), first entry (A00)
            - GRB1010B22: Grade B, Oct 10, entry B22

        Sequential logic:
            - Letter: A-Z (26 letters)
            - Number: 00-99 (100 numbers)
            - Total per day per grade: 26 * 100 = 2600 entries
        """
        # Extract grade letter (first letter of grade, uppercase)
        # If grade is "A" or "a", use 'A'. If "B" or "b", use 'B'
        grade_letter = self.grade[0].upper() if self.grade else 'A'

        # Get date in DDMM format (day and month)
        date_str = self.date.strftime('%d%m')

        # Get count of Floating entries for this grade on this date
        same_day_count = Floating.objects.filter(
            grade__istartswith=grade_letter,
            date=self.date
        ).count()

        # Calculate sequential code (Letter + 00-99)
        # Position in sequence (0-2599)
        position = same_day_count % 2600  # Reset after 2600 entries

        # Calculate letter index (A-Z, 26 letters)
        letter_index = position // 100  # Which letter (0-25)
        number = position % 100  # Which number (0-99)

        sequence_letter = chr(65 + letter_index)  # 65 is ASCII for 'A'
        sequence_number = f"{number:02d}"  # Format as 2 digits with leading zero

        # Combine: GR + {A/B} + DDMM + Letter + 00-99
        grade_id = f"GR{grade_letter}{date_str}{sequence_letter}{sequence_number}"

        return grade_id


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
    
class Drying(models.Model):
    """
    Daily drying tracking for coffee batches.
    Tracks daily progress with automated calculations and weekly lot consolidation.
    Filled daily from Monday to Sunday.
    """

    # User-provided fields
    processing_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Processing ID - can only be used Mon-Sun (locked after week ends)"
    )

    lot_id = models.CharField(
        max_length=10,
        help_text="Auto-generated lot ID (W01-W52 based on ISO week)"
    )

    date = models.DateField(
        default=timezone.now,
        help_text="Date of drying entry"
    )

    weather_condition = models.CharField(
        max_length=50,
        blank=True,
        help_text="Weather conditions (e.g., sunny, cloudy, drizzle)"
    )

    moisture_content = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Current day's moisture percentage (%)"
    )

    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Current day's weight (kg)"
    )

    moisture_before = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Previous day's moisture for rate calculation. Auto-filled after day 1."
    )

    weight_before = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Previous day's weight for rate calculation. Auto-filled after day 1."
    )

    # Auto-generated fields
    processing_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Auto-filled from processing_id (natural sundried, washed coffee, fermented)"
    )

    type_of_coffee = models.CharField(
        max_length=50,
        blank=True,
        help_text="Auto-filled from processing_id on day 1, then locked for same processing_id"
    )

    days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Auto-generated: days since processing_id creation or lot start"
    )

    moisture_deviation = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Auto-generated: moisture_content - 12 (ideal). E.g., +3 or -2"
    )

    rate_of_drying = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Auto-generated: moisture_before - moisture_content"
    )

    rate_of_weightloss = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Auto-generated: weight_before - weight"
    )

    outturn = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Auto-generated: percentage weight loss from first day"
    )

    outturn_deviation = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Auto-generated: outturn - 60 (target). E.g., +3 or -2"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-lot_id']
        verbose_name = "Daily Drying Record"
        verbose_name_plural = "Daily Drying Records"
        unique_together = [['processing_id', 'date'], ['lot_id', 'date']]

    def __str__(self):
        if self.processing_id:
            return f"{self.processing_id} - {self.date} (Lot: {self.lot_id})"
        else:
            return f"Lot {self.lot_id} - {self.date}"

    def save(self, *args, **kwargs):
        """
        Auto-generate fields before saving.
        Handles lot_id generation, auto-fills, and all calculations.
        """
        from datetime import datetime
        from django.utils import timezone as dj_timezone

        # Validate: processing_id and lot_id cannot both be set
        if self.processing_id and self.lot_id != self._generate_lot_id():
            # Allow: user provided custom lot_id
            pass

        # Generate lot_id if not provided (based on ISO week)
        if not self.lot_id:
            self.lot_id = self._generate_lot_id()

        # Auto-fill processing_type from processing_id
        if self.processing_id:
            # This assumes Processing model exists (to be added later)
            # For now, leave blank - will be filled by Processing model relationship
            pass

        # Auto-fill moisture_before and weight_before on day 2+ (same processing_id)
        if self.processing_id:
            previous_entry = Drying.objects.filter(
                processing_id=self.processing_id,
                date__lt=self.date
            ).order_by('-date').first()

            if previous_entry:
                # Day 2+: auto-fill if not manually provided
                if not self.moisture_before:
                    self.moisture_before = previous_entry.moisture_content
                if not self.weight_before:
                    self.weight_before = previous_entry.weight

        elif self.lot_id:
            # Monday entry (lot-based): use average/sum from previous week
            previous_entries = Drying.objects.filter(
                lot_id=self.lot_id,
                date__lt=self.date
            )

            if previous_entries.exists():
                # Not first entry of lot, so use averages/sums
                if not self.moisture_before:
                    avg_moisture = previous_entries.aggregate(
                        avg=models.Avg('moisture_content')
                    )['avg']
                    self.moisture_before = avg_moisture

                if not self.weight_before:
                    total_weight = previous_entries.aggregate(
                        total=models.Sum('weight')
                    )['total']
                    self.weight_before = total_weight

        # Calculate auto-generated fields
        self._calculate_deviations()
        self._calculate_rates()
        self._calculate_days()
        self._calculate_outturn()

        super().save(*args, **kwargs)

    def _generate_lot_id(self):
        """Generate lot_id as W01-W52 based on ISO week number."""
        from datetime import datetime
        iso_week = self.date.isocalendar()[1]
        return f"W{iso_week:02d}"

    def _calculate_deviations(self):
        """Calculate moisture and outturn deviations."""
        # Ideal moisture is 12%
        self.moisture_deviation = self.moisture_content - 12

    def _calculate_rates(self):
        """Calculate rate_of_drying and rate_of_weightloss."""
        if self.moisture_before:
            self.rate_of_drying = self.moisture_before - self.moisture_content
        else:
            self.rate_of_drying = 0

        if self.weight_before and self.weight:
            self.rate_of_weightloss = self.weight_before - self.weight
        else:
            self.rate_of_weightloss = 0

    def _calculate_days(self):
        """Calculate days since processing_id creation or lot start."""
        if self.processing_id:
            # Days since processing_id was created
            # This requires Processing model to have created_at field
            # For now, set to None (to be implemented when Processing model is updated)
            self.days = None
        elif self.lot_id:
            # Days since lot start (Monday of this week)
            from datetime import timedelta
            days_since_monday = self.date.weekday()  # Monday=0
            lot_start = self.date - timedelta(days=days_since_monday)
            self.days = (self.date - lot_start).days

    def _calculate_outturn(self):
        """Calculate outturn and outturn_deviation."""
        if self.processing_id:
            # Find first entry of this processing_id
            first_entry = Drying.objects.filter(
                processing_id=self.processing_id
            ).order_by('date').first()

            if first_entry and first_entry.weight and self.weight:
                first_weight = first_entry.weight
                outturn_pct = ((first_weight - self.weight) / first_weight) * 100
                self.outturn = outturn_pct
            else:
                self.outturn = 0

        elif self.lot_id:
            # Find sum of first-day weights for all processing_ids in this lot
            lot_entries = Drying.objects.filter(lot_id=self.lot_id).order_by('date')

            if lot_entries.exists():
                first_date = lot_entries.first().date
                first_day_entries = lot_entries.filter(date=first_date)
                total_first_weight = first_day_entries.aggregate(
                    total=models.Sum('weight')
                )['total'] or 0

                if total_first_weight and self.weight:
                    outturn_pct = ((total_first_weight - self.weight) / total_first_weight) * 100
                    self.outturn = outturn_pct
                else:
                    self.outturn = 0

        # Calculate outturn deviation (target is 60%)
        self.outturn_deviation = self.outturn - 60

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
