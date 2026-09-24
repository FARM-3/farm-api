from django.db import models
from django.conf import settings


class Warehouse(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=200, blank=True)
    capacity_kg = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.code} — {self.name}'


class InventoryLot(models.Model):
    STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('reserved', 'Reserved'),
        ('dispatched', 'Dispatched'),
        ('sold', 'Sold'),
    ]

    lot_id = models.CharField(max_length=50, unique=True)
    batch_id = models.CharField(max_length=50, blank=True)
    coffee_type = models.CharField(max_length=100, blank=True)
    grade = models.CharField(max_length=20, blank=True)
    total_kg = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bags = models.PositiveIntegerField(default=0)
    moisture_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='lots')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_stock')
    source_harvest_id = models.CharField(max_length=100, blank=True)
    qr_code = models.CharField(max_length=255, blank=True, help_text='Scan payload e.g. LOT:W38')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.lot_id} ({self.total_kg} kg)'


class DispatchNote(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    dispatch_id = models.CharField(max_length=30, unique=True)
    lot = models.ForeignKey(InventoryLot, on_delete=models.PROTECT, related_name='dispatches')
    sale = models.ForeignKey(
        'financialmanagement.Sale',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispatches',
    )
    buyer_name = models.CharField(max_length=200)
    buyer_contact = models.CharField(max_length=100, blank=True)
    quantity_kg = models.DecimalField(max_digits=12, decimal_places=2)
    bags = models.PositiveIntegerField(default=0)
    vehicle = models.CharField(max_length=50, blank=True)
    driver = models.CharField(max_length=120, blank=True)
    destination = models.CharField(max_length=200, blank=True)
    dispatch_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)
    proof_notes = models.TextField(blank=True, help_text='Gate proof — signature ref, photo note, etc.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-dispatch_date', '-created_at']

    def __str__(self):
        return f'{self.dispatch_id} → {self.buyer_name}'


class ExportComplianceDocument(models.Model):
    """Supporting documents for export due-diligence (prototype EUDR pack)."""

    DOC_TYPES = [
        ('land_title', 'Land title / tenure'),
        ('permit', 'Permit / licence'),
        ('photo_plot', 'Plot / geolocation photo'),
        ('contract', 'Purchase contract'),
        ('other', 'Other'),
    ]

    harvest_id = models.CharField(max_length=100, db_index=True)
    document_type = models.CharField(max_length=30, choices=DOC_TYPES, default='other')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='export_compliance/%Y/', blank=True, null=True)
    notes = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.harvest_id} — {self.title}'


class ExportTraceRecord(models.Model):
    """Trace Report — harvest lineage + compliance snapshot (replaces "dossier")."""

    record_id = models.CharField(max_length=30, unique=True)
    harvest_id = models.CharField(max_length=100)
    lot = models.ForeignKey(InventoryLot, null=True, blank=True, on_delete=models.SET_NULL, related_name='trace_records')
    dispatch = models.ForeignKey(DispatchNote, null=True, blank=True, on_delete=models.SET_NULL, related_name='trace_records')
    supplier_name = models.CharField(max_length=200, blank=True)
    origin_gps = models.CharField(max_length=100, blank=True)
    coffee_type = models.CharField(max_length=100, blank=True)
    total_kg = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    trace_data = models.JSONField(default=dict, blank=True)
    compliance_status = models.CharField(max_length=30, default='pending')
    compliance_notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.record_id} — {self.harvest_id}'
