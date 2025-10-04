from django.db import models

# Create your models here.
class Harvests(models.Model):
    cherry_color= models.AutoField(primary_key=True)
    date_of_harvest = models.CharField(max_length=100)
    quantity_harvest = models.CharField(max_length=200)
    crop_type = models.CharField(max_length=100)
    block = models.DateField()
    
    def __str__(self):
        return self.cherry_color



