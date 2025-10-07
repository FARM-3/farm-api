from django.db import models

# Create your models here.
class Harvests(models.Model):
    grade = models.CharField(max_length=100, blank=True)               # Grade of the harvest
    weight = models.CharField(max_length=100, blank=True)              # Weight of the harvest
    block = models.CharField(max_length=100, blank=True)               # Block of the harvest
    cherry_color = models.CharField(max_length=100, blank=True)        # Color of the cherry
    date = models.CharField(max_length=100, blank=True)               # Date of the harvest
    name = models.CharField(max_length=100, blank=True)               # Farmer's name
    amount_paid = models.CharField(max_length=100, blank=True)         # Amount paid to the farmer

    def __str__(self):
        return self.cherry_color



