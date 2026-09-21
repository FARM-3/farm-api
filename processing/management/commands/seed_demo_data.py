"""
Seed three end-to-end demo coffee stories for Tuesday presentation.
Run: python manage.py seed_demo_data
"""
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from aggregation.models import FarmerHarvest, FarmerRegistration
from production.models import Harvests
from processing.models import (
    Bagging,
    Drying,
    Floating,
    Ripeness,
    Washing,
)


class Command(BaseCommand):
    help = 'Seed demo farmers, harvests, and processing chains for export prototype demo'

    def handle(self, *args, **options):
        today = date.today()
        d1 = today - timedelta(days=14)
        d2 = today - timedelta(days=10)
        d3 = today - timedelta(days=5)

        self.stdout.write('Seeding demo data…')

        demo_harvests = ['FH-DEMO001', 'FH-DEMO002', 'ED0920PA1']
        demo_lots = ['W38-DEMO', 'W38-EST', 'W39-DEMO']
        Ripeness.objects.filter(harvest__in=demo_harvests).delete()
        Floating.objects.filter(harvest__in=demo_harvests).delete()
        Washing.objects.filter(processing_id__in=[f'{h}-WSH' for h in demo_harvests]).delete()
        Drying.objects.filter(lot_id__in=demo_lots).delete()
        Bagging.objects.filter(lot_id__in=demo_lots).delete()

        # --- Farmers ---
        farmer_defaults = {
            'coffee_variety': 'Arabica',
            'land_ownership': 'Owned',
            'source_of_seedlings': 'UCDA',
            'type_of_seedlings': ['Clonal'],
            'age_of_seedlings': '2 years',
            'irrigation_source': 'Rain-fed',
            'fertilizers': 'Organic compost',
            'pesticide': 'None',
            'spacing_between_trees': '3x3m',
        }
        FarmerRegistration.objects.update_or_create(
            farmer_id='RF-DEMO001',
            defaults={
                **farmer_defaults,
                'first_name': 'Grace',
                'last_name': 'Nakato',
                'gender': 'Female',
                'date_of_birth': date(1985, 3, 15),
                'farmer_type': 'Smallholder',
                'district': 'Kanungu',
                'parish': 'Kyeshero',
                'village': 'Rwenshama',
                'gps_coordinates': '0.9583,-29.7892',
                'contact': '0700123456',
            },
        )
        FarmerRegistration.objects.update_or_create(
            farmer_id='RF-DEMO002',
            defaults={
                **farmer_defaults,
                'coffee_variety': 'Robusta',
                'first_name': 'Peter',
                'last_name': 'Ssemwanga',
                'gender': 'Male',
                'date_of_birth': date(1978, 7, 22),
                'farmer_type': 'Smallholder',
                'district': 'Wakiso',
                'parish': 'Namayumba',
                'village': 'Bussi',
                'gps_coordinates': '0.4012,32.1456',
                'contact': '0700654321',
            },
        )

        def ensure_production_harvest(harvest_id, worker_name, weight, delivery_date, block_id='EXT'):
            """Production harvest row required by processing FK on Render DB."""
            Harvests.objects.update_or_create(
                harvest_id=harvest_id,
                defaults={
                    'worker_name': worker_name,
                    'block_id': block_id,
                    'weight_on_delivery': weight,
                    'date_of_delivery': delivery_date,
                    'amount_paid': Decimal('0.00'),
                    'paid_by': 'Admin',
                },
            )

        # --- Story 1: Complete aggregation harvest ---
        FarmerHarvest.objects.update_or_create(
            harvest_id='FH-DEMO001',
            defaults={
                'name': 'Grace Nakato',
                'coffee_type': 'Arabica',
                'weight_on_delivery': Decimal('1000.00'),
                'date_of_delivery': d1,
                'location_of_delivery': 'Main Farm Collection Point',
                'gps_coordinates_delivery': '0.9583,-29.7892',
                'price_per_kg': 4500,
                'amount_paid': Decimal('4500000.00'),
                'paid_by': 'Admin',
            },
        )
        ensure_production_harvest('FH-DEMO001', 'Grace Nakato', Decimal('1000.00'), d1, block_id='B01')

        Ripeness.objects.update_or_create(
            harvest='FH-DEMO001',
            defaults={
                'date': d1,
                'sample_size': 100,
                'no_of_redcherry': 92,
            },
        )
        Floating.objects.update_or_create(
            grade_id='FH-DEMO001-GRA',
            defaults={
                'harvest': 'FH-DEMO001',
                'grade': 'A',
                'weight': Decimal('820.00'),
                'date': d1,
            },
        )
        Floating.objects.update_or_create(
            grade_id='FH-DEMO001-GRB',
            defaults={
                'harvest': 'FH-DEMO001',
                'grade': 'B',
                'weight': Decimal('120.00'),
                'date': d1,
            },
        )
        Washing.objects.update_or_create(
            processing_id='FH-DEMO001-WSH',
            defaults={
                'grade_ids': ['FH-DEMO001-GRA'],
                'date': d2,
                'weight': Decimal('780.00'),
            },
        )
        for i, (dt, w, wb, out) in enumerate([
            (d2, Decimal('780.00'), Decimal('820.00'), Decimal('0')),
            (d2 + timedelta(days=3), Decimal('540.00'), Decimal('780.00'), Decimal('30.77')),
            (d3, Decimal('450.00'), Decimal('540.00'), Decimal('42.31')),
        ]):
            Drying.objects.update_or_create(
                processing_id='FH-DEMO001-WSH',
                date=dt,
                defaults={
                    'lot_id': 'W38-DEMO',
                    'weather_condition': 'sunny',
                    'moisture_content': Decimal('12.50') if i == 2 else Decimal('18.00'),
                    'weight': w,
                    'weight_before': wb,
                    'rate_of_weightloss': wb - w,
                    'outturn': out,
                    'processing_type': 'washed coffee',
                },
            )
        Bagging.objects.create(
            lot_id='W38-DEMO',
            date=timezone.make_aware(datetime.combine(d3, datetime.min.time())),
            weight=Decimal('420.00'),
            moisture_content=Decimal('11.50'),
            no_of_bags=14,
            qr_code='LOT:W38-DEMO',
            outturn=Decimal('42.00'),
        )

        # --- Story 2: Estate harvest (complete) ---
        ensure_production_harvest(
            'ED0920PA1', 'James Okello', Decimal('650.00'), d1, block_id='B01'
        )
        Harvests.objects.filter(harvest_id='ED0920PA1').update(
            amount_paid=Decimal('325000.00'),
        )
        Ripeness.objects.update_or_create(
            harvest='ED0920PA1',
            defaults={'date': d1, 'sample_size': 100, 'no_of_redcherry': 88},
        )
        Floating.objects.update_or_create(
            grade_id='ED0920PA1-GRA',
            defaults={
                'harvest': 'ED0920PA1',
                'grade': 'A',
                'weight': Decimal('520.00'),
                'date': d1,
            },
        )
        Washing.objects.update_or_create(
            processing_id='ED0920PA1-WSH',
            defaults={
                'grade_ids': ['ED0920PA1-GRA'],
                'date': d2,
                'weight': Decimal('500.00'),
            },
        )
        Drying.objects.update_or_create(
            processing_id='ED0920PA1-WSH',
            date=d3,
            defaults={
                'lot_id': 'W38-EST',
                'weather_condition': 'sunny',
                'moisture_content': Decimal('12.00'),
                'weight': Decimal('280.00'),
                'weight_before': Decimal('500.00'),
                'outturn': Decimal('46.15'),
                'processing_type': 'washed coffee',
            },
        )
        Bagging.objects.create(
            lot_id='W38-EST',
            date=timezone.make_aware(datetime.combine(d3, datetime.min.time())),
            weight=Decimal('280.00'),
            moisture_content=Decimal('12.00'),
            no_of_bags=9,
            qr_code='LOT:W38-EST',
        )

        # --- Story 3: In-progress farmer harvest ---
        FarmerHarvest.objects.update_or_create(
            harvest_id='FH-DEMO002',
            defaults={
                'name': 'Peter Ssemwanga',
                'coffee_type': 'Robusta',
                'weight_on_delivery': Decimal('750.00'),
                'date_of_delivery': d2,
                'location_of_delivery': 'Bussi Collection Centre',
                'gps_coordinates_delivery': '0.4012,32.1456',
                'price_per_kg': 3800,
                'amount_paid': Decimal('2850000.00'),
                'paid_by': 'Admin',
            },
        )
        ensure_production_harvest('FH-DEMO002', 'Peter Ssemwanga', Decimal('750.00'), d2)
        Ripeness.objects.update_or_create(
            harvest='FH-DEMO002',
            defaults={'date': d2, 'sample_size': 100, 'no_of_redcherry': 85},
        )
        Floating.objects.update_or_create(
            grade_id='FH-DEMO002-GRA',
            defaults={
                'harvest': 'FH-DEMO002',
                'grade': 'A',
                'weight': Decimal('600.00'),
                'date': d2,
            },
        )
        Washing.objects.update_or_create(
            processing_id='FH-DEMO002-WSH',
            defaults={
                'grade_ids': ['FH-DEMO002-GRA'],
                'date': d3,
                'weight': Decimal('580.00'),
            },
        )
        Drying.objects.update_or_create(
            processing_id='FH-DEMO002-WSH',
            date=today - timedelta(days=1),
            defaults={
                'lot_id': 'W39-DEMO',
                'weather_condition': 'cloudy',
                'moisture_content': Decimal('22.00'),
                'weight': Decimal('520.00'),
                'weight_before': Decimal('580.00'),
                'processing_type': 'washed coffee',
            },
        )

        self.stdout.write(self.style.SUCCESS(
            'Demo data seeded: FH-DEMO001 (complete), ED0920PA1 (estate complete), FH-DEMO002 (in progress)'
        ))
        self.stdout.write('Recommended demo harvests: FH-DEMO001, ED0920PA1, FH-DEMO002')
