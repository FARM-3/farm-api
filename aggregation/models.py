from django.db import models

# Create your models here.
class Farmer(models.Model):
    name = models.CharField(max_length=100, blank=True)               # Farmer's name
    location = models.CharField(max_length=200, blank=True)           # Farmer's location
    num_trees = models.CharField(max_length=100,default=0, blank=True)       # Count of trees (only positive numbers)
    contact = models.CharField(max_length=100, blank=True)            # Contact details (phone/email/etc.)

    def __str__(self):
        return self.name
    
    #Farmerharvest model
class FarmerHarvest(models.Model):
    name = models.CharField(max_length=100)               # Farmer's name
    weight_on_delivery = models.IntegerField(max_length=100)         # Weight of the harvest
    weight_after_floating = models.IntegerField(max_length=100)       # Weight after floating
    date_of_delivery = models.CharField(max_length=100)    # Date of delivery
    grade = models.CharField(max_length=100)               # Grade of the harvest
    cherry_color = models.CharField(max_length=100)        # Color of the cherry
    stage = models.CharField(max_length=100)               # Stage of processing
    amount_paid = models.CharField(max_length=100)         # Amount paid to the farmer
    paid_by = models.CharField(max_length=100)             # Entity that made the payment
    id = models.CharField(max_length=100, primary_key=True)          # Unique identifier for the harvest

    def __str__(self):
        return self.name            
    