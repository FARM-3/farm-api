from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
import random
import requests

# Create your models here.
class FarmerRegistration(models.Model):
    """GENDER_CHOICES = [
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
    ]"""
    first_name = models.CharField(max_length=100)              
    last_name = models.CharField(max_length=100)             
    gender = models.CharField(max_length=10, blank=False)  
    nin = models.CharField(
        max_length=14,
        unique=True,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^[A-Z0-9]{14}$', message='NIN must be 14 characters: uppercase letters and digits only.')],
        help_text="Enter 14 characters (A–Z, 0–9); leave empty if not available"
    )                     # National Identification Number
    date_of_birth = models.DateField()        
    contact = models.CharField(max_length=20, blank=True, null=True)            
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)        
    farmer_type = models.CharField(max_length=15, blank=False)  

    
    started_coffee_farming_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(2010)],
        help_text="Enter the year you started coffee farming (optional)"
    )

    #location details
    """DISTRICT_CHOICES = [
        ('WAKISO', 'Wakiso'),
        ('OTHER', 'Other'),
    ]
    SUB_COUNTY_CHOICES = [
        ('NAMAYUMBA', 'NAMAYUMBA'),
        ('BUSUKUMA', 'BUSUKUMA'),
        ('GOMBE', 'GOMBE'),
        ('KATABI', 'KATABI'),
        ('KAKIRI', 'KAKIRI'),
        ('KASANJE', 'KASANJE'),
        ('KAJJANSI', 'KAJJANSI'),
        ('MASULIITA', 'MASULIITA'),
        ('MENDE', 'MENDE'),
        ('NANSABO', 'NANSABO'),
        ('NSANGI', 'NSANGI'),
        ('SSISA', 'SSISA'),
        ('BUSSI', 'BUSSI'),
        ('NBWERU', 'NBWERU'),
        ('OTHER', 'Other'),
    ]"""


    district = models.CharField(max_length=100, blank=True)         # District                  # If 'Other', specify
    sub_county = models.CharField(max_length=100, blank=True)                 # If 'Other', specify
    parish = models.CharField(max_length=100, blank=True)             # Parish                    # If 'Other', specify
    village = models.CharField(max_length=100, blank=True)          # Village
    gps_coordinates = models.CharField(max_length=100, blank=True) # GPS coordinates
    nearest_landmark = models.CharField(max_length=100, blank=True) # Nearest landmark
    farmer_id = models.CharField(max_length=100, primary_key=True)          # Unique identifier for the farmer

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.farmer_id or 'New'})"

    def save(self, *args, **kwargs):
        
        self.full_clean()

        
        if not self.farmer_id:
            
            
            first_initial = self.first_name[0].upper() if self.first_name else 'X'
            last_initial = self.last_name[0].upper() if self.last_name else 'X'
            
            # Generate 3 random digits
            random_digits = ''.join(random.choices('0123456789', k=3))
            
            # Assemble the unique ID
            new_unique_id = f"{first_initial}{last_initial}{random_digits}A"
            
            # Check if this generated ID already exists in the database
            
            while FarmerRegistration.objects.filter(farmer_id=new_unique_id).exists():
                
                random_digits = ''.join(random.choices('0123456789', k=3))
                new_unique_id = f"{first_initial}{last_initial}{random_digits}A"
            
            # Assign the unique ID
            self.farmer_id = new_unique_id
        
        
        if not self.gps_coordinates:
            try:
                parts = [
                    (self.village or ''),
                    (self.other_parish or self.parish or ''),
                    (self.other_sub_county or self.sub_county or ''),
                    (self.other_district or self.district or ''),
                    'Uganda'
                ]
                query = ', '.join([p for p in parts if p])
                if query:
                    resp = requests.get(
                        'https://nominatim.openstreetmap.org/search',
                        params={'q': query, 'format': 'json', 'limit': 1},
                        headers={'User-Agent': 'Rugyeyo-Farm-API/1.0'}
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if isinstance(data, list) and data:
                            lat = data[0].get('lat')
                            lon = data[0].get('lon')
                            if lat and lon:
                                self.gps_coordinates = f"{lat},{lon}"
            except Exception:
                
                pass

        super().save(*args, **kwargs)

        
    coffee_variety = models.CharField(max_length=100, blank=False)     
    number_of_trees = models.PositiveIntegerField(default=0)         
    ownership_of_trees = models.BooleanField(default=True)    
    
    planted_date = models.DateField(null=True, blank=True)            
    land_ownership = models.CharField(max_length=100, blank=False)         
    spacing_between_trees = models.CharField(max_length=100)  
    defforestation_status = models.BooleanField(default=True)      

    #source of seedlings
    source_of_seedlings = models.CharField(max_length=100, blank=False)      
    type_of_seedlings = models.CharField(max_length=100, blank=False)     
    age_of_seedlings = models.CharField(max_length=100, blank=False)          
    standard_practices = models.BooleanField(default=False) 
    irrigation_source = models.CharField(max_length=100, blank=False)       

    #agro-chemicals used
    fertilizers = models.CharField(max_length=100, blank=False)       
    pesticide = models.CharField(max_length=100, blank=False)         



    
    #Farmerharvest model
class FarmerHarvest(models.Model):
    name = models.CharField(max_length=100)
    coffee_type = models.CharField(max_length=100, null=True)       # Type of coffee
    weight_on_delivery = models.IntegerField(null=True)         # Weight of the harvest
    date_of_delivery = models.CharField(max_length=100, null=True)    # Date of delivery
    price_per_kg = models.IntegerField(null=True)               # Price per kg of the harvest
    amount_paid = models.CharField(max_length=100, null=True)         # Amount paid to the farmer
    paid_by = models.CharField(max_length=100, null=True)             # Entity that made the payment
    harvest_id = models.CharField(max_length=100, primary_key=True)          # Unique identifier for the harvest
    no_of_bags = models.IntegerField(null=True)               # Number of bags delivered

    def __str__(self):
        return f"{self.name} ({self.harvest_id})"
               
    