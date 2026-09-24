"""
Master demo seed — run before presentations to fill empty tables.
Usage: python manage.py seed_demo_all
"""
from datetime import date, timedelta
from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from aggregation.models import FarmerRegistration
from configuration.models import FarmAsset, LookupOption, ConfigCategory
from configuration.services import apply_sale_item_rates
from export_ops.models import DispatchNote, InventoryLot, Warehouse
from financialmanagement.models import Customer, Expense, Sale, Setprice, Staff, Wage
from production.models import Block
from taskmanagement.models import Season, Task
from users.models import User


SALE_ITEM_RATES = {
    'Green Coffee': ('5000', 'kg'),
    'Roasted Coffee': ('8000', 'kg'),
    'Coffee Cherry': ('2500', 'kg'),
    'Parchment': ('4500', 'kg'),
    'Hulled Coffee': ('5500', 'kg'),
}


class Command(BaseCommand):
    help = 'Seed all demo data for FMIS presentation (config, blocks, finance, tasks, export)'

    def handle(self, *args, **options):
        self.stdout.write('=== FMIS demo seed (all sections) ===')

        call_command('seed_config_defaults')
        call_command('seed_suppliers')
        call_command('seed_fertilizer_types')
        call_command('seed_coffee_types')
        call_command('seed_permissions')
        call_command('seed_demo_compliance')
        apply_sale_item_rates(SALE_ITEM_RATES)

        manager, _ = User.objects.get_or_create(
            phone='0700000001',
            defaults={'name': 'Demo Manager', 'role': 'manager', 'is_active': True},
        )
        if not manager.has_usable_password():
            manager.set_password('1234')
            manager.save(update_fields=['password'])

        User.objects.get_or_create(
            phone='0700000002',
            defaults={'name': 'Block Champion Demo', 'role': 'block_champion', 'is_active': True},
        )
        bc = User.objects.get(phone='0700000002')
        if not bc.has_usable_password():
            bc.set_password('1234')
            bc.save(update_fields=['password'])

        today = date.today()
        blocks = [
            ('B01', 420, 'Arabica', 'KR-01'),
            ('B02', 380, 'Arabica', 'SL14'),
            ('B03', 510, 'Robusta', 'KR-02'),
            ('B04', 290, 'Arabica', 'KP423'),
            ('B05', 450, 'Robusta', 'Screen 18'),
            ('B06', 320, 'Arabica', 'Nyasaland'),
        ]
        for block_id, trees, coffee, seedling in blocks:
            Block.objects.update_or_create(
                block_id=block_id,
                defaults={
                    'no_of_trees': trees,
                    'date_planted': date(2018, 3, 1),
                    'type_of_coffee': coffee,
                    'source_of_seedling': 'UCDA Nursery',
                    'type_of_seedling': seedling,
                    'age_of_seedling': 2,
                    'fertilizers': 'Organic',
                    'fertilizer_names': 'Bird Droppings, Compost',
                    'use_pesticides': 'Yes',
                    'pesticides_list': 'Copper oxychloride',
                    'standard_practices': 'Mulching, Pruning',
                    'created_by': manager,
                },
            )
        self.stdout.write(f'  blocks: {len(blocks)}')

        staff_specs = [
            ('James', 'Okello', 'Male', 'fulltime'),
            ('Sarah', 'Namutebi', 'Female', 'fulltime'),
            ('David', 'Mugisha', 'Male', 'parttime'),
        ]
        for i, (fn, ln, gender, etype) in enumerate(staff_specs, start=1):
            nin = f'CM{i:02d}DEMO{i:06d}'
            Staff.objects.update_or_create(
                nin=nin,
                defaults={
                    'first_name': fn,
                    'last_name': ln,
                    'gender': gender,
                    'district': 'Kanungu',
                    'sub_county': 'Kyeshero',
                    'parish': 'Rwenshama',
                    'village': 'Rugyeyo',
                    'date_hired': date(2020, 1, 15),
                    'employment_type': etype,
                    'monthly_salary': 450000 if etype == 'fulltime' else 200000,
                    'is_active': True,
                },
            )
        self.stdout.write(f'  staff: {len(staff_specs)}')

        customers = [
            ('Kampala Coffee Exporters Ltd', '0700111222', 'Kampala'),
            ('Mountain Brew Co-op', '0700333444', 'Mbarara'),
            ('Green Bean Traders', '0700555666', 'Entebbe'),
        ]
        for name, phone, city in customers:
            Customer.objects.update_or_create(
                name=name,
                defaults={'phone': phone, 'city': city, 'country': 'Uganda', 'is_active': True},
            )
        self.stdout.write(f'  customers: {len(customers)}')

        cust = Customer.objects.first()
        sales_specs = [
            ('Green Coffee', 50, 5000, today - timedelta(days=5)),
            ('Parchment', 120, 4500, today - timedelta(days=12)),
            ('Roasted Coffee', 30, 8000, today - timedelta(days=20)),
        ]
        for item, qty, rate, pay_date in sales_specs:
            amount = Decimal(qty) * Decimal(rate)
            Sale.objects.get_or_create(
                item=item,
                date_of_payment=pay_date,
                quantity=qty,
                defaults={
                    'customer': cust,
                    'first_name': cust.name.split()[0] if cust else 'Demo',
                    'last_name': 'Buyer',
                    'rate': rate,
                    'amount': amount,
                    'total_amount': amount,
                    'balance': Decimal('0'),
                    'status': 'Paid',
                    'method_of_payment': 'Bank Transfer',
                },
            )
        self.stdout.write(f'  sales: {len(sales_specs)}')

        expense_specs = [
            ('Tractor fuel — Block B01', 'Fuel & Transport', 850000, today - timedelta(days=3)),
            ('NPK fertilizer purchase', 'Chemicals & Inputs', 1200000, today - timedelta(days=18)),
            ('Staff protective gear', 'General Supplies', 320000, today - timedelta(days=25)),
            ('Extension training session', 'Training', 450000, today - timedelta(days=40)),
        ]
        for name, category, amount, exp_date in expense_specs:
            Expense.objects.get_or_create(
                expense_name=name,
                date=exp_date,
                defaults={
                    'category': category,
                    'item': name.split('—')[0].strip()[:50],
                    'supplier': 'Rugyeyo Suppliers',
                    'description': name,
                    'amount': amount,
                    'unit_cost': amount,
                    'quantity': 1,
                    'location': 'Rugyeyo Farm',
                },
            )
        self.stdout.write(f'  expenses: {len(expense_specs)}')

        staff = Staff.objects.first()
        if staff:
            Wage.objects.get_or_create(
                employee_name=staff.get_full_name(),
                date_of_payment=today - timedelta(days=7),
                defaults={'staff': staff, 'amount_paid': 180000, 'days_missed': 0},
            )

        Setprice.objects.get_or_create(
            id=1,
            defaults={'production_kgPrice': '5000', 'farmer_kgPrice': '4500'},
        )

        FarmAsset.objects.get_or_create(
            asset_id='AST-DEMO-01',
            defaults={
                'name': 'Tractor — Massey Ferguson',
                'asset_type': 'vehicle',
                'location': 'Main shed',
                'purchase_date': date(2019, 6, 1),
                'purchase_value': Decimal('45000000'),
                'current_value': Decimal('32000000'),
                'condition': 'Good',
                'is_active': True,
            },
        )
        FarmAsset.objects.get_or_create(
            asset_id='AST-DEMO-02',
            defaults={
                'name': 'Coffee pulper',
                'asset_type': 'equipment',
                'location': 'Processing yard',
                'purchase_value': Decimal('8500000'),
                'current_value': Decimal('6000000'),
                'condition': 'Good',
                'is_active': True,
            },
        )

        season, _ = Season.objects.get_or_create(
            name='2026 Main Crop',
            defaults={
                'season_type': 'harvest',
                'start_date': date(2026, 3, 1),
                'end_date': date(2026, 8, 31),
                'description': 'Primary harvest season demo',
                'created_by': manager,
            },
        )
        block = Block.objects.filter(block_id='B01').first()
        task_specs = [
            ('Cherry collection — B01', ['harvest'], 'high', False),
            ('Pruning follow-up — B02', ['pruning'], 'medium', False),
            ('Fertilizer application — B03', ['fertilizing'], 'medium', True),
        ]
        for title, activities, priority, completed in task_specs:
            Task.objects.get_or_create(
                title=title,
                date=today + timedelta(days=2),
                defaults={
                    'description': f'Demo task: {title}',
                    'activity': activities,
                    'priority': priority,
                    'assigned_to': [],
                    'created_by': manager,
                    'block': block,
                    'season': season,
                    'completed': completed,
                    'completed_at': timezone.now() if completed else None,
                },
            )
        self.stdout.write(f'  tasks: {len(task_specs)}')

        wh, _ = Warehouse.objects.get_or_create(
            code='WH-MAIN',
            defaults={'name': 'Main Export Warehouse', 'location': 'Rugyeyo', 'capacity_kg': Decimal('50000'), 'is_active': True},
        )
        lot, _ = InventoryLot.objects.update_or_create(
            lot_id='W38-DEMO',
            defaults={
                'batch_id': 'BA001',
                'coffee_type': 'Arabica Washed',
                'grade': 'A',
                'total_kg': Decimal('1200'),
                'bags': 24,
                'moisture_pct': Decimal('11.5'),
                'warehouse': wh,
                'status': 'in_stock',
                'source_harvest_id': 'FH-DEMO001',
                'qr_code': 'LOT:W38-DEMO',
            },
        )
        DispatchNote.objects.get_or_create(
            dispatch_id='DSP-DEMO-001',
            defaults={
                'lot': lot,
                'buyer_name': 'Kampala Coffee Exporters Ltd',
                'buyer_contact': '0700111222',
                'quantity_kg': Decimal('600'),
                'bags': 12,
                'vehicle': 'UBH 123A',
                'driver': 'John Driver',
                'destination': 'Kampala',
                'dispatch_date': today - timedelta(days=2),
                'status': 'in_transit',
                'created_by': manager,
                'notes': 'Partial dispatch demo shipment',
            },
        )

        call_command('seed_field_ops_demo')
        call_command('seed_demo_data')

        farmer_count = FarmerRegistration.objects.count()
        sale_items = LookupOption.objects.filter(category=ConfigCategory.SALE_ITEM, is_active=True).count()
        self.stdout.write(self.style.SUCCESS(
            f'Demo seed complete — {Block.objects.count()} blocks, {sale_items} sale items with rates, '
            f'{farmer_count} farmers, export lot {lot.lot_id}'
        ))
