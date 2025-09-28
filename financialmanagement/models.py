from django.db import models

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

