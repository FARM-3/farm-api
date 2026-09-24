from django.db import models


class ConfigCategory(models.TextChoices):
    COFFEE_TYPE = 'coffee_type', 'Coffee Type'
    COFFEE_VARIETY = 'coffee_variety', 'Coffee Variety'
    FERTILIZER = 'fertilizer', 'Fertilizer'
    FERTILIZER_ORGANIC = 'fertilizer_organic', 'Organic Fertilizer Products'
    FERTILIZER_INORGANIC = 'fertilizer_inorganic', 'Inorganic Fertilizer Products'
    EXPENSE_CATEGORY = 'expense_category', 'Expense Category'
    PESTICIDE = 'pesticide', 'Pesticide'
    STANDARD_PRACTICE = 'standard_practice', 'Standard Practice'
    SEEDLING_TYPE = 'seedling_type', 'Seedling Type'
    GRADE = 'grade', 'Grade'
    SPACING = 'spacing', 'Tree Spacing'
    SALE_ITEM = 'sale_item', 'Sale Item'


class LookupOption(models.Model):
    """Configurable dropdown values — replace hardcoded farm-specific lists."""

    category = models.CharField(max_length=50, choices=ConfigCategory.choices)
    value = models.CharField(max_length=120)
    label = models.CharField(max_length=120, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    default_rate = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True,
        help_text='Default unit price (UGX) — used for sale items',
    )
    unit_label = models.CharField(
        max_length=20, blank=True, default='kg',
        help_text='Unit of measure label (kg, unit, etc.)',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'sort_order', 'value']
        unique_together = [('category', 'value')]
        verbose_name = 'Lookup Option'
        verbose_name_plural = 'Lookup Options'

    def __str__(self):
        return f'{self.category}: {self.display_label}'

    @property
    def display_label(self):
        return self.label or self.value


class CoffeeType(models.Model):
    """Parent coffee type (like Grade in payroll) — has sub-types."""

    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class FertilizerType(models.Model):
    """Parent fertilizer type — Organic, Inorganic, Mixed, etc."""

    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class FertilizerSubType(models.Model):
    """Product under a fertilizer type (e.g. NPK under Inorganic)."""

    fertilizer_type = models.ForeignKey(FertilizerType, on_delete=models.CASCADE, related_name='sub_types')
    name = models.CharField(max_length=120)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'name']
        unique_together = [('fertilizer_type', 'name')]

    def __str__(self):
        return f'{self.fertilizer_type.name} / {self.name}'


class CoffeeSubType(models.Model):
    """Sub-type under a coffee type (like Spine under Grade)."""

    coffee_type = models.ForeignKey(CoffeeType, on_delete=models.CASCADE, related_name='sub_types')
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=30, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'name']
        unique_together = [('coffee_type', 'name')]

    def __str__(self):
        return f'{self.coffee_type.name} / {self.name}'


class FarmAsset(models.Model):
    """Simple FMIS asset register."""

    ASSET_TYPES = [
        ('equipment', 'Equipment'),
        ('vehicle', 'Vehicle'),
        ('building', 'Building'),
        ('tool', 'Tool'),
        ('other', 'Other'),
    ]

    asset_id = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES, default='equipment')
    location = models.CharField(max_length=200, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    condition = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.asset_id} — {self.name}'


class FarmDocument(models.Model):
    """Licences, certificates, contracts — compliance document store."""

    DOC_TYPES = [
        ('license', 'License'),
        ('certificate', 'Certificate'),
        ('contract', 'Contract'),
        ('audit', 'Audit Report'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('pending', 'Pending'),
    ]

    doc_id = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=200)
    doc_type = models.CharField(max_length=20, choices=DOC_TYPES, default='certificate')
    issuer = models.CharField(max_length=200, blank=True)
    reference_no = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to='documents/%Y/%m/', blank=True, null=True)
    file_url = models.URLField(blank=True, help_text='Legacy external URL; prefer file upload')
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expiry_date', 'title']

    def __str__(self):
        return self.title


class TrainingRecord(models.Model):
    """Farmer/staff training sessions — relevant for extension & compliance."""

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    training_id = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=200, blank=True)
    trainer = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    attendees = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title
