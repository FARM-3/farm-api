
# Create your models here.

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date



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


class Batch(models.Model):
    """
    Batch model - groups multiple grade IDs together for batch processing
    """
    batch_id = models.CharField(
        max_length=20,
        unique=True,
        primary_key=True,
        help_text="Format: BA001, BA002, etc."
    )

    # Store grade_ids as JSON array
    grade_ids = models.JSONField(
        help_text="Array of grade_ids included in this batch"
    )

    created_by = models.CharField(
        max_length=100,
        help_text="User who created the batch"
    )

    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes about the batch"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Batch"
        verbose_name_plural = "Batches"

    def __str__(self):
        return f"{self.batch_id} ({len(self.grade_ids)} grades)"


class Fermenting(models.Model):
    """
    Fermenting process - tracks coffee batches during fermentation
    Can process either a single grade_id or multiple grade_ids (batch)
    """
    # Processing ID - provided by frontend
    processing_id = models.CharField(
        max_length=50,
        unique=True,
        editable=True,
        primary_key=True,
        help_text="Frontend-generated: FER{DDMM}{SEQ} (e.g., FER041200)"
    )

    # Store grade_ids as JSON array to support both single and batch processing
    grade_ids = models.JSONField(
        default=list,
        help_text="Array of grade IDs being processed (can be single or multiple)"
    )

    # Optional: Keep backward compatibility with old ForeignKey field
    # This will be deprecated - use grade_ids instead
    grade = models.ForeignKey(
        'Floating',
        on_delete=models.PROTECT,
        related_name='fermenting_processes',
        null=True,
        blank=True,
        help_text="DEPRECATED: Use grade_ids instead. Single grade ID from Floating quality control test"
    )

    # Fermentation period
    start_date = models.DateField(
        default=timezone.now,
        help_text="Date when fermentation started"
    )

    end_date = models.DateField(
        default=timezone.now,
        help_text="Date when fermentation ended"
    )

    # Duration in days (auto-calculated from dates)
    days = models.PositiveIntegerField(
        editable=False,
        help_text="Number of days for fermentation (auto-calculated)"
    )

    # Weight after fermenting
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Weight in kg after fermentation"
    )

    # Metadata fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-end_date']
        verbose_name = "Fermenting Process"
        verbose_name_plural = "Fermenting Processes"

    def __str__(self):
        grade_count = len(self.grade_ids) if isinstance(self.grade_ids, list) else 1
        return f"{self.processing_id} - {grade_count} grade(s)"

    def save(self, *args, **kwargs):
        """Calculate days before saving (processing_id comes from frontend)"""
        # Auto-calculate days from start_date and end_date
        if self.start_date and self.end_date:
            self.days = (self.end_date - self.start_date).days

        super().save(*args, **kwargs)

class Washing(models.Model):
    """
    Washing process - tracks coffee batches during washing
    Can process either a single grade_id or multiple grade_ids (batch)
    """
    # Processing ID - auto-generated unique identifier
    processing_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        primary_key=True,
        help_text="Auto-generated: WASH-{YYYYMMDD}-{SEQ}"
    )

    # Store grade_ids as JSON array to support both single and batch processing
    grade_ids = models.JSONField(
        default=list,
        help_text="Array of grade IDs being processed (can be single or multiple)"
    )

    # Optional: Keep backward compatibility with old ForeignKey field
    grade = models.ForeignKey(
        'Floating',
        on_delete=models.PROTECT,
        related_name='washing_processes',
        null=True,
        blank=True,
        help_text="DEPRECATED: Use grade_ids instead"
    )

    # Washing date
    date = models.DateField(
        default=timezone.now,
        help_text="Date when washing was performed"
    )

    # Weight after washing
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Weight in kg after washing"
    )

    # Metadata fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Washing Process"
        verbose_name_plural = "Washing Processes"

    def __str__(self):
        grade_count = len(self.grade_ids) if isinstance(self.grade_ids, list) else 1
        return f"{self.processing_id} - {grade_count} grade(s)"

    def save(self, *args, **kwargs):
        """Auto-generate processing_id before saving"""
        # Auto-generate processing_id if not exists
        if not self.processing_id:
            self.processing_id = self.generate_processing_id()

        super().save(*args, **kwargs)

    def generate_processing_id(self):
        """
        Generate processing_id in format: WASH-{YYYYMMDD}-{SEQ}
        Example: WASH-20250114-001
        """
        from datetime import date
        today = date.today().strftime('%Y%m%d')

        # Get count of Washing entries for this date
        same_day_count = Washing.objects.filter(
            date=self.date
        ).count()

        # Sequential number
        sequence = f"{same_day_count + 1:03d}"

        return f"WASH-{today}-{sequence}"


class NaturalSundrying(models.Model):
    """
    Natural Sundrying process - tracks coffee batches during natural sun drying
    Can process either a single grade_id or multiple grade_ids (batch)
    """
    # Processing ID - auto-generated unique identifier
    processing_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        primary_key=True,
        help_text="Auto-generated: SUND-{YYYYMMDD}-{SEQ}"
    )

    # Store grade_ids as JSON array to support both single and batch processing
    grade_ids = models.JSONField(
        default=list,
        help_text="Array of grade IDs being processed (can be single or multiple)"
    )

    # Optional: Keep backward compatibility with old ForeignKey field
    grade = models.ForeignKey(
        'Floating',
        on_delete=models.PROTECT,
        related_name='sundrying_processes',
        null=True,
        blank=True,
        help_text="DEPRECATED: Use grade_ids instead"
    )

    # Sundrying start date
    start_date = models.DateField(
        default=timezone.now,
        help_text="Date when sundrying started"
    )

    # Weight before sundrying
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Weight in kg before sundrying"
    )

    # Metadata fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Natural Sundrying Process"
        verbose_name_plural = "Natural Sundrying Processes"

    def __str__(self):
        grade_count = len(self.grade_ids) if isinstance(self.grade_ids, list) else 1
        return f"{self.processing_id} - {grade_count} grade(s)"

    def save(self, *args, **kwargs):
        """Auto-generate processing_id before saving"""
        # Auto-generate processing_id if not exists
        if not self.processing_id:
            self.processing_id = self.generate_processing_id()

        super().save(*args, **kwargs)

    def generate_processing_id(self):
        """
        Generate processing_id in format: SUND-{YYYYMMDD}-{SEQ}
        Example: SUND-20250114-001
        """
        from datetime import date
        today = date.today().strftime('%Y%m%d')

        # Get count of Sundrying entries for this date
        same_day_count = NaturalSundrying.objects.filter(
            start_date=self.start_date
        ).count()

        # Sequential number
        sequence = f"{same_day_count + 1:03d}"

        return f"SUND-{today}-{sequence}"
    
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

    # Calculated fields (now editable - calculated on frontend in offline-first approach)
    processing_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Calculated on frontend from processing_id (natural sundried, washed coffee, fermented)"
    )

    type_of_coffee = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Calculated on frontend from processing_id on day 1"
    )

    days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Calculated on frontend: days since processing_id creation or lot start"
    )

    moisture_deviation = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
        help_text="Calculated on frontend: moisture_content - 12 (ideal)"
    )

    rate_of_drying = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
        help_text="Calculated on frontend: moisture_before - moisture_content"
    )

    rate_of_weightloss = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
        help_text="Calculated on frontend: weight_before - weight"
    )

    outturn = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
        help_text="Calculated on frontend: percentage weight loss from first day"
    )

    outturn_deviation = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
        help_text="Calculated on frontend: outturn - 60 (target)"
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
        Simplified save for offline-first approach.
        Frontend handles all calculations and business logic.
        Backend simply stores the data.
        """
        # Generate lot_id if not provided (based on ISO week)
        if not self.lot_id:
            self.lot_id = self._generate_lot_id()

        super().save(*args, **kwargs)

    def _generate_lot_id(self):
        """Generate lot_id as W01-W52 based on ISO week number."""
        iso_week = self.date.isocalendar()[1]
        return f"W{iso_week:02d}"


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
        default='W01',
        help_text="Lot id from drying (select existing drying lot_id)"
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.01,
        validators=[MinValueValidator(0.01)],
        help_text="Weight in kilograms"
    )
    moisture_content = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=12.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Moisture content percentage (0-100)"
    )
    no_of_bags = models.PositiveIntegerField(
        default=1,
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

    def save(self, *args, **kwargs):
        """
        Simplified save for offline-first approach.
        Frontend handles all validation and calculations.
        Backend simply stores the data as-is.
        """
        super().save(*args, **kwargs)
# ...existing code...       