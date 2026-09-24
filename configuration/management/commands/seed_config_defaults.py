"""Seed default lookup options — generic coffee farm values, not Rugyeyo-specific."""

from django.core.management.base import BaseCommand
from configuration.models import LookupOption, ConfigCategory
from configuration.services import apply_sale_item_rates

DEFAULTS = {
    ConfigCategory.COFFEE_TYPE: ['Arabica', 'Robusta', 'Liberica'],
    ConfigCategory.COFFEE_VARIETY: ['Arabica', 'Robusta', 'Liberica'],
    ConfigCategory.FERTILIZER: ['Organic', 'Inorganic', 'Mixed'],
    ConfigCategory.FERTILIZER_ORGANIC: [
        'Bird Droppings', 'Rabbit Urine', 'Compost', 'Manure', 'Coffee pulp',
    ],
    ConfigCategory.FERTILIZER_INORGANIC: [
        'NPK', 'Urea', 'DAP', 'CAN', 'Single Super Phosphate',
    ],
    ConfigCategory.PESTICIDE: [
        'None', 'Striker', 'Fungicide', 'Copper-based', 'Neem oil', 'Biological control',
    ],
    ConfigCategory.STANDARD_PRACTICE: [
        'Inter-cropping', 'Pruning', 'Mulching', 'Stumping', 'Agro-forestry',
        'Fertilizing', 'Pest control', 'Shade management',
        'Stamping', 'Spot Weeding', 'Desuckering', 'Slashing',
    ],
    ConfigCategory.SEEDLING_TYPE: [
        'KR-01', 'KR-02', 'KR-03', 'KR-04', 'KR-05',
        'CWDR-01', 'CWDR-02', 'CWDR-03', 'CWDR-04', 'CWDR-05',
    ],
    ConfigCategory.GRADE: ['A', 'B', 'C', 'D'],
    ConfigCategory.SPACING: [
        '3 metres by 3 metres',
        '2.4 metres by 2.4 metres',
        '2 metres by 1 metres',
    ],
    ConfigCategory.SALE_ITEM: [
        'Green Coffee', 'Roasted Coffee', 'Coffee Cherry', 'Parchment', 'Hulled Coffee',
    ],
    ConfigCategory.EXPENSE_CATEGORY: [
        'General Supplies', 'Fuel & Transport', 'Labour', 'Equipment', 'Utilities',
        'Maintenance', 'Chemicals & Inputs', 'Training', 'Aggregation', 'Other',
    ],
}

SALE_ITEM_RATES = {
    'Green Coffee': ('5000', 'kg'),
    'Roasted Coffee': ('8000', 'kg'),
    'Coffee Cherry': ('2500', 'kg'),
    'Parchment': ('4500', 'kg'),
    'Hulled Coffee': ('5500', 'kg'),
}


class Command(BaseCommand):
    help = 'Seed default configurable lookup options for FARM FMIS'

    def handle(self, *args, **options):
        created = 0
        for category, values in DEFAULTS.items():
            for idx, val in enumerate(values):
                defaults = {'label': val, 'sort_order': idx, 'is_active': True}
                if category == ConfigCategory.SALE_ITEM and val in SALE_ITEM_RATES:
                    rate, unit = SALE_ITEM_RATES[val]
                    defaults['default_rate'] = rate
                    defaults['unit_label'] = unit
                _, was_created = LookupOption.objects.update_or_create(
                    category=category,
                    value=val,
                    defaults=defaults,
                )
                if was_created:
                    created += 1
        apply_sale_item_rates(SALE_ITEM_RATES)
        self.stdout.write(self.style.SUCCESS(f'Seeded {created} new lookup options; sale rates applied.'))
