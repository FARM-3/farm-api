from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.conf import settings

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


class Block(models.Model):
    """Block Details Model"""
    
    block_id = models.CharField(max_length=50, unique=True, primary_key=True)
    no_of_trees = models.IntegerField(validators=[MinValueValidator(0)])
    date_planted = models.DateField()
    type_of_coffee = models.CharField(max_length=100)
    source_of_seedling = models.CharField(max_length=200)
    type_of_seedling = models.CharField(max_length=200)
    age_of_seedling = models.IntegerField(validators=[MinValueValidator(0)])
    use_pesticides = models.CharField(max_length=255)
    pesticides_list = models.TextField(blank=True, null=True)
    standard_practices = models.CharField(max_length=255)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='blocks_created')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.block_id}"



