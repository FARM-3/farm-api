from django.db import models

# Create your models here.
class Farmer(models.Model):
    name = models.CharField(max_length=100)               # Farmer's name
    location = models.CharField(max_length=200)           # Farmer's location
    num_trees = models.PositiveIntegerField()       # Count of trees (only positive numbers)
    contact = models.CharField(max_length=100)            # Contact details (phone/email/etc.)

    def __str__(self):
        return self.name
    
    #Farmerharvest model
class FarmerHarvest(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    harvest = models.CharField(max_length=100)
    date_harvested = models.DateField()
    quantity = models.FloatField()

    def __str__(self):
        return f"{self.farmer.name} - {self.harvest.cherry_color} - {self.date_harvested}"