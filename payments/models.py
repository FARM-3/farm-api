from django.db import models
from django.utils import timezone


class IPNRegistration(models.Model):
	"""Stores IPN registrations returned by Pesapal when calling RegisterIPNURL."""
	ipn_id = models.CharField(max_length=128, unique=True)
	url = models.URLField()
	ipn_notification_type = models.CharField(max_length=10, choices=(('GET', 'GET'), ('POST', 'POST')))
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"IPN {self.ipn_id} -> {self.url}"


class PaymentOrder(models.Model):
	"""Represents an order/submission from your app to Pesapal.

	'merchant_reference' maps to the 'id' you send in SubmitOrderRequest and
	can be used to link an order in your system.
	"""
	merchant_reference = models.CharField(max_length=128, blank=True, null=True, db_index=True)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	currency = models.CharField(max_length=8, default='UGX')
	description = models.TextField(blank=True)
	callback_url = models.URLField(blank=True, null=True)
	notification = models.ForeignKey(IPNRegistration, on_delete=models.SET_NULL, null=True, blank=True)
	billing_address = models.JSONField(blank=True, null=True)
	account_number = models.CharField(max_length=128, blank=True, null=True)
	subscription_details = models.JSONField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Order {self.merchant_reference or self.pk} ({self.amount} {self.currency})"


class PaymentTransaction(models.Model):
	"""Stores the status/details returned by Pesapal for an order (GetTransactionStatus / IPN)."""
	order = models.ForeignKey(PaymentOrder, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
	order_tracking_id = models.UUIDField(unique=True)
	merchant_reference = models.CharField(max_length=128, blank=True, null=True)
	amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	currency = models.CharField(max_length=8, blank=True, null=True)
	confirmation_code = models.CharField(max_length=128, blank=True, null=True)
	payment_method = models.CharField(max_length=64, blank=True, null=True)
	payment_status_description = models.CharField(max_length=128, blank=True, null=True)
	status_code = models.IntegerField(default=0)
	payment_account = models.CharField(max_length=64, blank=True, null=True)
	call_back_url = models.URLField(blank=True, null=True)
	subscription_transaction_info = models.JSONField(blank=True, null=True)
	raw_response = models.JSONField(blank=True, null=True)
	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"Txn {self.order_tracking_id} status={self.status_code}"


class Subscription(models.Model):
	"""Represents a recurring subscription created via Pesapal.

	Note: Pesapal will create and manage schedules; we store a local representation
	to track business logic (deliveries, cancellations, etc.).
	"""
	FREQUENCY_CHOICES = (
		('DAILY', 'Daily'),
		('WEEKLY', 'Weekly'),
		('MONTHLY', 'Monthly'),
		('YEARLY', 'Yearly'),
	)

	account_reference = models.CharField(max_length=128)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	currency = models.CharField(max_length=8, default='UGX')
	frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
	start_date = models.DateField()
	end_date = models.DateField()
	correlation_id = models.CharField(max_length=128, blank=True, null=True)
	active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Subscription {self.account_reference} {self.frequency} {self.amount}{self.currency}"


class Refund(models.Model):
	"""Represents a refund request made to Pesapal."""
	payment_transaction = models.ForeignKey(PaymentTransaction, on_delete=models.SET_NULL, null=True, blank=True)
	confirmation_code = models.CharField(max_length=128)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	username = models.CharField(max_length=128)
	remarks = models.TextField(blank=True)
	status = models.CharField(max_length=32, blank=True, null=True)
	message = models.TextField(blank=True, null=True)
	raw_response = models.JSONField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Refund {self.confirmation_code} {self.amount} ({self.status})"


class OrderCancellation(models.Model):
	"""Represents a cancellation request made to Pesapal for an order."""
	payment_transaction = models.ForeignKey(PaymentTransaction, on_delete=models.SET_NULL, null=True, blank=True)
	order_tracking_id = models.UUIDField()
	status = models.CharField(max_length=32, blank=True, null=True)
	message = models.TextField(blank=True, null=True)
	raw_response = models.JSONField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Cancel {self.order_tracking_id} ({self.status})"
