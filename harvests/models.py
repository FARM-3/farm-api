from django.db import models

# Create your models here.
class Harvests(models.Model):
    grade = models.CharField(max_length=100)               # Grade of the harvest
    weight = models.CharField(max_length=100)              # Weight of the harvest
    block = models.CharField(max_length=100)               # Block of the harvest
    cherry_color = models.CharField(max_length=100)        # Color of the cherry
    date = models.CharField(max_length=100)               # Date of the harvest
    name = models.CharField(max_length=100)               # Farmer's name
    amount_paid = models.CharField(max_length=100)         # Amount paid to the farmer

    def __str__(self):
        return self.cherry_color



