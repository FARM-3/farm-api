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
    name = models.CharField(max_length=100, blank=True)               # Farmer's name
    weight_note = models.CharField(max_length=100,blank=True)          # Weight of the harvest
    date_of_delivery = models.CharField(max_length=100,blank=True)    # Date of delivery
    grade = models.CharField(max_length=100, blank=True)               # Grade of the harvest
    cherry_color = models.CharField(max_length=100, blank=True)        # Color of the cherry
    stage = models.CharField(max_length=100, blank=True)               # Stage of processing
    amount_paid = models.CharField(max_length=100, blank=True)         # Amount paid to the farmer
    paid_by = models.CharField(max_length=100, blank=True)             # Entity that made the payment
    id = models.CharField(max_length=100, primary_key=True) # Unique identifier for the harvest

    def __str__(self):
        return self.name            
    