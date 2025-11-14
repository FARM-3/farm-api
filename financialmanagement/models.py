from django.db import models, transaction
from decimal import Decimal
from django.core.validators import RegexValidator

# Create your models here.
# class StaffRegistration(models.Model):
#     staff_id = models.CharField(max_length=20, unique=True, primary_key=True)
#     first_name = models.CharField(max_length=50)
#     last_name = models.CharField(max_length=50)
#     gender = models.CharField(max_length=10)
#     nin = models.CharField(max_length=14, unique=True, null=True, blank=True)
#     district = models.CharField(max_length=50)
#     sub_county = models.CharField(max_length=50)
#     parish = models.CharField(max_length=50)
#     village = models.CharField(max_length=50)
#     date_hired = models.DateField()
#     employment_type = models.CharField(max_length=20)
#     contact = models.CharField(max_length=20, null=True, blank=True)

#     class Meta:
#         verbose_name = "Staff Registration"
#         verbose_name_plural = "Staff Registrations"
#         ordering = ['last_name', 'first_name']

#     def __str__(self):
#         return f"{self.first_name} {self.last_name} ({self.staff_id})"
    
#     @property
#     def full_name(self):
#         return f"{self.first_name} {self.last_name}"

class Staff(models.Model):
    """
    Staff model for managing employees who process payments
    Includes personal information and employment details
    """
    
    # Employment type choices
    # EMPLOYMENT_TYPE_CHOICES = [
    #     ('fulltime', 'Full Time'),
    #     ('parttime', 'Part Time'),
    # ]
    
    # Auto-generated staff ID (e.g., RF001, RF002, etc.)
    staff_id = models.CharField(
        max_length=10,
        unique=True,
        editable=False,
        primary_key=True,
        help_text="Auto-generated ID: RF + 3-digit number"
    )
    
    # Personal Information
    first_name = models.CharField(
        max_length=100,
        help_text="Staff member's first name"
    )
    
    last_name = models.CharField(
        max_length=100,
        help_text="Staff member's last name"
    )
    
    # National Identification Number
    nin = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9]+$',
                message='NIN should contain only uppercase letters and numbers'
            )
        ],
        help_text="National ID Number (unique identifier)"
    )
    
    # Location Information
    district = models.CharField(
        max_length=100,
        help_text="District where staff member resides"
    )
    
    sub_county = models.CharField(
        max_length=100,
        help_text="Sub-county where staff member resides"
    )
    
    parish = models.CharField(
        max_length=100,
        help_text="Parish where staff member resides"
    )
    
    village = models.CharField(
        max_length=100,
        help_text="Village where staff member resides"
    )
    
    gender = models.CharField(
        max_length=100,
        help_text="Gender of a worker"
    )

    # Employment Information
    date_hired = models.DateField(
        help_text="Date when staff member was hired"
    )
    
    employment_type = models.CharField(
        max_length=100,
        help_text="Type of employment contract"
    )
    
    # Status tracking
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the staff member is currently active"
    )
    
    # Timestamp fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    monthly_salary = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Staff Member'
        verbose_name_plural = 'Staff Members'
        indexes = [
            models.Index(fields=['nin']),
            models.Index(fields=['last_name', 'first_name']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employment_type})"
    def save(self, *args, **kwargs):
        """
        Override save to auto-generate staff_id before saving
        """
        if not self.staff_id:
            self.staff_id = self.generate_staff_id()
        super().save(*args, **kwargs)

    def generate_staff_id(self):
        """
        Generate staff ID in format: RF + 3-digit number
        - RF: Prefix for staff
        - 3-digit number: Sequential number starting from 001
        Uses atomic transaction to prevent duplicate IDs
        """
        with transaction.atomic():
            # Use select_for_update to lock the table and prevent race conditions
            latest_staff = Staff.objects.select_for_update().order_by('-staff_id').first()

            if latest_staff and latest_staff.staff_id.startswith('RF'):
                try:
                    # Extract the number from the last staff_id (e.g., "RF003" -> 3)
                    last_number = int(latest_staff.staff_id[2:])
                    sequence_number = last_number + 1
                except (ValueError, IndexError):
                    # Fallback if extraction fails
                    sequence_number = Staff.objects.count() + 1
            else:
                # If no staff exists, start from 1
                sequence_number = Staff.objects.count() + 1

            # Generate 3-digit number (001, 002, ..., 999)
            formatted_number = f"{sequence_number:03d}"

            # Combine prefix and number
            staff_id = f"RF{formatted_number}"

            return staff_id
    
    def get_full_name(self):
        """
        Return the staff member's full name
        """
        return f"{self.first_name} {self.last_name}"
    
    def get_full_address(self):
        """
        Return the complete address of the staff member
        """
        return f"{self.village}, {self.parish}, {self.sub_county}, {self.district}"


class Wage(models.Model):
    # Free-text employee name (can be any name)
    employee_name = models.CharField(
        max_length=255,
        help_text="Employee name (can be any name)",
        blank=True,
        null=True
    )

    # Optional link to registered staff
    staff = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        related_name='wages',
        null=True,
        blank=True,
        help_text="Link to registered staff member (optional)"
    )

    days_missed = models.IntegerField( help_text="Number of days a staff member missed", default=0)
    amount_paid = models.IntegerField()
    date_of_payment = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = "Wage Payment"
        verbose_name_plural = "Wage Payments"
        ordering = ['-date_of_payment']

    def __str__(self):
        name = self.employee_name if self.employee_name else "Unknown"
        return f"Wages for {name} - {self.amount_paid}"

    def save(self, *args, **kwargs):
        """
        Override save to add any custom logic
        """
        # Ensure values are not negative
        if self.amount_paid < 0:
            raise ValueError("Amount paid cannot be negative")
        if self.days_missed < 0:
            raise ValueError("Days missed cannot be negative")

        super().save(*args, **kwargs)
    
class Sale(models.Model):

    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    batch_id = models.CharField(max_length=20, null=True, blank=True)
    item = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_of_payment = models.DateField()
    status = models.CharField(max_length=20, default="paid")
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    method_of_payment = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Sale Record"
        verbose_name_plural = "Sale Records"
        ordering = ['-date_of_payment', 'last_name', 'first_name']

    def __str__(self):
        customer_name = f"{self.first_name} {self.last_name}".strip() 
        return f"Sale to {customer_name} of {self.item}"

    def get_customer_name(self):
        """Return the customer's full name"""
        return f"{self.first_name} {self.last_name}".strip() 

    def save(self, *args, **kwargs):
        self.total_amount = self.rate * self.quantity

        self.balance = self.total_amount - self.amount
        
        # 3. Update status based on balance
        if self.balance <= 0:
            self.status = "Paid"
        elif self.amount > 0 and self.balance > 0:
            self.status = "Partial Payment"
        else:
            self.status = "Pending"
            
        super().save(*args, **kwargs)

class Receipt(models.Model):
    sale = models.OneToOneField(Sale, on_delete=models.PROTECT, related_name='receipt_info')
    receipt_number = models.CharField(max_length=20, unique=True)
    date_issued = models.DateField(auto_now_add=True)
    is_voided = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Receipt"
        verbose_name_plural = "Receipts"
        ordering = ['-date_issued', 'receipt_number']

    def __str__(self):
        return f"Receipt {self.receipt_number} for {self.sale.get_customer_name()}"

class Expense(models.Model):
    expense_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    item = models.CharField(max_length=50)
    supplier = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    location = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"
        ordering = ['-date']

    def __str__(self):
        return f"Expense: {self.description} - {self.amount}"
    
class Balancesheet(models.Model):
    BALANCE_CHOICES = [
        ('A', 'Asset'),
        ('L', 'Liability'),
        ('E', 'Equity'),
    ]

    account_name = models.CharField(
        max_length=100,
        help_text="Name of the account (e.g., 'Cash', 'Accounts Receivable', etc.)"
    )
    account_type = models.CharField(max_length=1, choices=BALANCE_CHOICES)
    balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="The current balance of this account."
    )

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Account Balance"
        verbose_name_plural = "Account Balances"
        # Group accounts together for easier reading
        ordering = ['account_type', 'account_type']

    def __str__(self):
        return f"{self.account_name} ({self.get_account_type_display()}): ${self.balance}"


class Setprice(models.Model):
    production_kgPrice = models.CharField(max_length=10)
    farmer_kgPrice = models.CharField(max_length=10)

    class Meta:
        verbose_name = "Price Setting"
        verbose_name_plural = "Price Settings"
        ordering = ['-id']

    def __str__(self):
        return f"Production Price: {self.production_kgPrice}, Farmer Price: {self.farmer_kgPrice}"