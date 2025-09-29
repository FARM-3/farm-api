from django.db import models
from decimal import Decimal


# Create your models here.
class Wage(models.Model):
    employee_name = models.CharField(max_length=20)
    days_worked = models.IntegerField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    date_of_payment = models.DateField()
    monthly_pay = models.DecimalField(max_digits=10, decimal_places=2)
    deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    noted_reason = models.CharField(max_length=255, default="", blank=True)


    class Meta:
        verbose_name = "Wage Payment"
        verbose_name_plural = "Wage Payments"
        ordering = ['-date_of_payment', 'employee_name']

    def __str__(self):
        return f"Wages for {self.employee_name} - {self.deduction}"
    
    @property
    def calculate_net_salary(self):
        return self.monthly_pay - self.deduction

<<<<<<< HEAD

=======
>>>>>>> a48265d (created Sale and Expense APIs)
class Sale(models.Model):
    customer_name = models.CharField(max_length=20)
    item = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_of_payment = models.DateField()
    status = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    method_of_payment = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Sale Record"
        verbose_name_plural = "Sale Records"
        ordering = ['-date_of_payment', 'customer_name']

    def __str__(self):
        return f"Sale to {self.customer_name} of {self.item}"

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
