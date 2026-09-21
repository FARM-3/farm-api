"""Seed default lookup options — generic coffee farm values, not Rugyeyo-specific."""

from django.core.management.base import BaseCommand
from configuration.models import LookupOption, ConfigCategory

DEFAULTS = {
    ConfigCategory.COFFEE_TYPE: ['Arabica', 'Robusta', 'Liberica'],
    ConfigCategory.COFFEE_VARIETY: ['Arabica', 'Robusta', 'Liberica'],
    ConfigCategory.FERTILIZER: ['Organic', 'Inorganic', 'Mixed', 'Compost', 'NPK'],
    ConfigCategory.PESTICIDE: ['None', 'Copper-based', 'Neem oil', 'Biological control'],
    ConfigCategory.STANDARD_PRACTICE: [
        'Inter-cropping', 'Pruning', 'Mulching', 'Stumping',
        'Agro-forestry', 'Fertilizing', 'Pest control', 'Shade management',
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
}


class Command(BaseCommand):
    help = 'Seed default configurable lookup options for FARM FMIS'

    def handle(self, *args, **options):
        created = 0
        for category, values in DEFAULTS.items():
            if LookupOption.objects.filter(category=category).exists():
                self.stdout.write(f'  skip {category} (already seeded)')
                continue
            for idx, val in enumerate(values):
                LookupOption.objects.create(
                    category=category,
                    value=val,
                    label=val,
                    sort_order=idx,
                    is_active=True,
                )
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Seeded {created} lookup options'))
