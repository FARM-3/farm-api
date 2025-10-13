from django.db import models
import random

# Create your models here.
class FarmerRegistration(models.Model):
    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ]

    FARMER_TYPE_CHOICES = [
        ('COOPERATIVE', 'Co-operative Farmer'),
        ('INDIVIDUAL', 'Individual Farmer'),
    ]
    COFFEE_VARIETY_CHOICES = [
        ('ARABICA', 'Arabica'),
        ('ROBUSTA', 'Robusta'),
        ('LAIBERICA', 'Laiberica'),
        # Add a default 'None' or 'Other' option if necessary
    ]
    LAND_OWNERSHIP_CHOICES = [
        ('FREEHOLD', 'Freehold'),
        ('MAILO', 'Mailo'),
        ('CUSTOMARY', 'Customary'),
        ('LEASEHOLD', 'Leasehold'),
    ]
    SEEDLING_SOURCE_CHOICES = [
        ('NURSERY', 'Nursery'),
        ('GOVERNMENT', 'Government'),
        ('CO-OPERATIVES', 'Co-operatives'),
        ('OTHER', 'Other'),
    ]
    STANDARD_PRACTICES_CHOICES = [
        ('BENDING', 'Bending'),
        ('PRUNING', 'Pruning'),
        ('WEEDING', 'Weeding'),
        ('STUMPING', 'Stumping'),
        ('STEMING', 'Steming'),
        ('MULCHING', 'Mulching'),
    ]
    FERTILIZER_CHOICES = [
        ('ORGANIC', 'Organic'),
        ('INORGANIC', 'Inorganic'),
    ]
    first_name = models.CharField(max_length=100, blank=True)               # Farmer's name
    last_name = models.CharField(max_length=100, blank=True)                # Farmer's name
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)  # Farmer
    nin = models.CharField(max_length=14,unique=True, blank=True)                     # National Identification Number
    date_of_birth = models.DateField()         # Date of birth
    contact = models.CharField(max_length=20, blank=True)            # Contact details (phone/email/etc.)
    email = models.EmailField(max_length=100, unique=True)          # Email address
    farmer_type = models.CharField(max_length=15, choices=FARMER_TYPE_CHOICES)  # Type of farmer

    #location details
    district = models.CharField(max_length=100, blank=True)         # District
    county = models.CharField(max_length=100, blank=True)           # County
    sub_county = models.CharField(max_length=100, blank=True)       # Sub-county
    parish = models.CharField(max_length=100, blank=True)           # Parish
    village = models.CharField(max_length=100, blank=True)          # Village
    gps_coordinates = models.CharField(max_length=100, blank=True) # GPS coordinates
    nearest_landmark = models.CharField(max_length=100, blank=True) # Nearest landmark
    farmer_id = models.CharField(max_length=100, primary_key=True)          # Unique identifier for the farmer

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.farmer_unique_id or 'New'})"

    def save(self, *args, **kwargs):
        # 1. Ensure the model is fully validated (important for cleaning/setting data)
        self.full_clean() 

        # 2. Auto-generate unique ID only if it's a new record (no primary key or ID is missing)
        if not self.pk or not self.farmer_unique_id:
            
            # Ensure names exist before trying to access their first letter
            first_initial = self.first_name[0].upper() if self.first_name else 'X'
            last_initial = self.last_name[0].upper() if self.last_name else 'X'
            
            # Generate 3 random digits
            random_digits = ''.join(random.choices('0123456789', k=3))
            
            # Assemble the unique ID
            new_unique_id = f"{first_initial}{last_initial}{random_digits}A"
            
            # Check if this generated ID already exists in the database
            # This is critical to ensure uniqueness
            while FarmerRegistration.objects.filter(farmer_unique_id=new_unique_id).exists():
                # If it exists, generate a new set of random digits and try again
                random_digits = ''.join(random.choices('0123456789', k=3))
                new_unique_id = f"{first_initial}{last_initial}{random_digits}A"
            
            # Assign the unique ID
            self.farmer_unique_id = new_unique_id
        
        super().save(*args, **kwargs)

        #coffee details
    coffee_variety = models.CharField(choices=COFFEE_VARIETY_CHOICES)       # Coffee variety
    number_of_trees = models.PositiveIntegerField(default=0)          # Number of trees under coffee cultivation
    ownership_of_trees = models.BooleanField(default=True)      # Ownership status of the trees
    planted_date = models.DateField()            # Date when the trees were planted
    land_ownership = models.CharField(choices=LAND_OWNERSHIP_CHOICES)         # Land ownership details
    spacing_between_trees = models.CharField(max_length=100)  # Spacing between trees
    defforestation_status = models.BooleanField(default=True)      # Deforestation status

    #source of seedlings
    source_of_seedlings = models.CharField(choices=SEEDLING_SOURCE_CHOICES)      # Source of seedlings
    type_of_seedlings = models.CharField(choices=COFFEE_VARIETY_CHOICES)          # Type of seedlings
    age_of_seedlings = models.CharField(max_length=100)          # Age of seedlings
    standard_practices = models.BooleanField(choices=STANDARD_PRACTICES_CHOICES) # Whether standard practices are followed
    irrigation_source = models.CharField(max_length=100)        # Source of irrigation

    #agro-chemicals used
    fertilizers = models.CharField(max_length=100)        # Fertilizers used
    pesticide = models.CharField(max_length=100)          # Pesticides used



    
    #Farmerharvest model
class FarmerHarvest(models.Model):
    name = models.CharField(max_length=100)               # Farmer's name
    weight_on_delivery = models.IntegerField(max_length=100, null=True)         # Weight of the harvest
    weight_after_floating = models.IntegerField(max_length=100, null=True)       # Weight after floating
    date_of_delivery = models.CharField(max_length=100, null=True)    # Date of delivery
    grade = models.CharField(max_length=100, null=True)               # Grade of the harvest
    cherry_color = models.CharField(max_length=100, null=True)        # Color of the cherry
    stage = models.CharField(max_length=100, null=True)               # Stage of processing
    amount_paid = models.CharField(max_length=100, null=True)         # Amount paid to the farmer
    paid_by = models.CharField(max_length=100, null=True)             # Entity that made the payment
    id = models.CharField(max_length=100, primary_key=True)       # Unique identifier for the harvest

    def __str__(self):
        return self.name            
    