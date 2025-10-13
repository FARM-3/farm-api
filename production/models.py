from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Harvests(models.Model):
    """
    Model to track coffee harvests from workers
    Harvest ID is auto-generated based on worker name, date, and submission sequence
    """
    
    # Block choices - six predefined blocks
    BLOCK_CHOICES = [
        ('block01', 'Block 01'),
        ('block02', 'Block 02'),
        ('block03', 'Block 03'),
        ('block04', 'Block 04'),
        ('block05', 'Block 05'),
        ('block06', 'Block 06'),
    ]
    
    # Auto-generated harvest ID (e.g., ED0711PA1)
    harvest_id = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False,
        primary_key=True,
        help_text="Auto-generated ID: WorkerInitials + DDMM + P + SequenceCode"
    )
    
    # Worker bringing the harvest
    worker_name = models.CharField(
        max_length=100,
        help_text="Name of the worker delivering the harvest"
    )
    
    # Block where harvest was collected
    block_id = models.CharField(
        max_length=10,
        choices=BLOCK_CHOICES,
        help_text="Block identifier where coffee was harvested"
    )
    
    # Weight with two decimal places
    weight_on_delivery = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Weight of harvest in kg (2 decimal places)"
    )
    
    # Date of delivery
    date_of_delivery = models.DateField(
        help_text="Date when harvest was delivered"
    )
    
    # Payment amount
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount paid to worker"
    )
    
    # Staff member who processed payment (Foreign Key to Staff model)
    paid_by = models.ForeignKey(
        'financialmanagement.Staff',  # Reference to Staff in financialmanagement app
        on_delete=models.PROTECT,  # Prevent deletion of staff with payment records
        related_name='payments_processed',
        help_text="Staff member who processed the payment"
    )
    
    # Timestamp fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_of_delivery', '-created_at']
        verbose_name = 'Harvest'
        verbose_name_plural = 'Harvests'
    
    def __str__(self):
        return f"{self.harvest_id} - {self.worker_name}"
    
    def save(self, *args, **kwargs):
        """
        Override save to auto-generate harvest_id before saving
        """
        if not self.harvest_id:
            self.harvest_id = self.generate_harvest_id()
        super().save(*args, **kwargs)
    
    def generate_harvest_id(self):
        """
        Generate harvest ID in format: XX + DDMM + P + LN
        - XX: First two letters of worker_name (uppercase)
        - DDMM: Day and month from date_of_delivery
        - P: Production indicator
        - LN: Letter-Number sequence (A0-Z9, then resets)
        """
        # Get first two letters of worker name (uppercase)
        worker_initials = ''.join(filter(str.isalpha, self.worker_name[:2])).upper()
        if len(worker_initials) < 2:
            worker_initials = worker_initials.ljust(2, 'X')  # Pad with X if name too short
        
        # Get date in DDMM format
        date_str = self.date_of_delivery.strftime('%d%m')
        
        # Production indicator
        prod_indicator = 'P'
        
        # Get sequence code (A0-Z9)
        sequence_code = self.get_next_sequence()
        
        # Combine all parts
        harvest_id = f"{worker_initials}{date_str}{prod_indicator}{sequence_code}"
        
        return harvest_id
    
    @staticmethod
    def get_next_sequence():
        """
        Generate the next sequence code (A0-Z9 pattern, resets after Z9)
        Returns a string like 'A0', 'A1', ..., 'Z9'
        """
        # Get the count of all harvests to determine sequence
        count = Harvests.objects.count()
        
        # Calculate letter (A-Z, 26 letters) and number (0-9, 10 numbers)
        # Total combinations: 26 * 10 = 260, then resets
        position = count % 260  # Reset after 260 entries
        
        letter_index = position // 10  # Which letter (0-25)
        number = position % 10          # Which number (0-9)
        
        letter = chr(65 + letter_index)  # 65 is ASCII for 'A'
        
        return f"{letter}{number}"


