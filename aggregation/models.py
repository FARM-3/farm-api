from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
import random
import requests

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
    nin = models.CharField(
        max_length=14,
        unique=True,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^[A-Z0-9]{14}$', message='NIN must be 14 characters: uppercase letters and digits only.')],
        help_text="Enter 14 characters (A–Z, 0–9); leave empty if not available"
    )                     # National Identification Number
    date_of_birth = models.DateField()         # Date of birth
    contact = models.CharField(max_length=20, blank=True, null=True)            # Contact details (optional)
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)          # Email address (optional)
    farmer_type = models.CharField(max_length=15, choices=FARMER_TYPE_CHOICES)  # Type of farmer

    # Section 1 end question: Which year did you start coffee farming?
    started_coffee_farming_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(2010)],
        help_text="Enter the year you started coffee farming (optional)"
    )

    #location details
    DISTRICT_CHOICES = [
        ('WAKISO', 'Wakiso'),
        ('OTHER', 'Other'),
    ]
    SUB_COUNTY_CHOICES = [
        ('NAMAYUMBA', 'Masaka'),
        ('BUSUKUMA', 'Wakiso'),
        ('GOMBE', 'Mbale'),
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
    ]


    district = models.CharField(max_length=100, blank=True, choices=DISTRICT_CHOICES)         # District
    other_district = models.CharField(max_length=100, blank=True, null=True)                  # If 'Other', specify
    sub_county = models.CharField(max_length=100, blank=True, choices=SUB_COUNTY_CHOICES)     # Sub-county
    other_sub_county = models.CharField(max_length=100, blank=True, null=True)                # If 'Other', specify
    parish = models.CharField(max_length=100, blank=True)             # Parish                    # If 'Other', specify
    village = models.CharField(max_length=100, blank=True)          # Village
    gps_coordinates = models.CharField(max_length=100, blank=True) # GPS coordinates
    nearest_landmark = models.CharField(max_length=100, blank=True) # Nearest landmark
    farmer_id = models.CharField(max_length=100, primary_key=True)          # Unique identifier for the farmer

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.farmer_id or 'New'})"

    def save(self, *args, **kwargs):
        # 1. Ensure the model is fully validated (important for cleaning/setting data)
        self.full_clean()

        # 2. Auto-generate farmer_id only if it's missing
        if not self.farmer_id:
            
            # Ensure names exist before trying to access their first letter
            first_initial = self.first_name[0].upper() if self.first_name else 'X'
            last_initial = self.last_name[0].upper() if self.last_name else 'X'
            
            # Generate 3 random digits
            random_digits = ''.join(random.choices('0123456789', k=3))
            
            # Assemble the unique ID
            new_unique_id = f"{first_initial}{last_initial}{random_digits}A"
            
            # Check if this generated ID already exists in the database
            # This is critical to ensure uniqueness
            while FarmerRegistration.objects.filter(farmer_id=new_unique_id).exists():
                # If it exists, generate a new set of random digits and try again
                random_digits = ''.join(random.choices('0123456789', k=3))
                new_unique_id = f"{first_initial}{last_initial}{random_digits}A"
            
            # Assign the unique ID
            self.farmer_id = new_unique_id
        
        # 3. Auto-generate GPS coordinates if missing, using OpenStreetMap Nominatim
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
                # Silently ignore geocoding failures to avoid blocking saves
                pass

        super().save(*args, **kwargs)

        #coffee details
    coffee_variety = models.CharField(choices=COFFEE_VARIETY_CHOICES)       # Coffee variety
    number_of_trees = models.PositiveIntegerField(default=0)          # Number of trees under coffee cultivation
    ownership_of_trees = models.BooleanField(default=True)      # Do you own all these trees? (Yes/No)

    # If ownership_of_trees is Yes, capture month and year planted (optional)
    
    planted_date = models.DateField(null=True, blank=True)            # Legacy field; kept for compatibility
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
    weight_on_delivery = models.IntegerField(max_length=100)         # Weight of the harvest
    weight_after_floating = models.IntegerField(max_length=100)       # Weight after floating
    date_of_delivery = models.CharField(max_length=100)    # Date of delivery
    grade = models.CharField(max_length=100)               # Grade of the harvest
    cherry_color = models.CharField(max_length=100)        # Color of the cherry
    stage = models.CharField(max_length=100)               # Stage of processing
    amount_paid = models.CharField(max_length=100)         # Amount paid to the farmer
    paid_by = models.CharField(max_length=100)             # Entity that made the payment
    id = models.CharField(max_length=100, primary_key=True)       # Unique identifier for the harvest

    def __str__(self):
        return self.name            
    