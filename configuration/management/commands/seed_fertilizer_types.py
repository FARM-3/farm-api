from django.core.management.base import BaseCommand
from configuration.models import FertilizerType, FertilizerSubType
from configuration.services import sync_fertilizer_lookups_from_types

DEFAULTS = {
    'Organic': [
        'Bird Droppings', 'Rabbit Urine', 'Compost', 'Manure', 'Coffee pulp',
    ],
    'Inorganic': [
        'NPK', 'Urea', 'DAP', 'CAN', 'Single Super Phosphate', 'Striker',
    ],
    'Mixed': [
        'NPK + Compost blend', 'Organic + Urea mix',
    ],
}


class Command(BaseCommand):
    help = 'Seed fertilizer types with nested products (sub-types)'

    def handle(self, *args, **options):
        created = 0
        for idx, (name, products) in enumerate(DEFAULTS.items()):
            ft, ft_created = FertilizerType.objects.get_or_create(
                name=name,
                defaults={'sort_order': idx, 'is_active': True},
            )
            if ft_created:
                created += 1
            existing = {s.name for s in ft.sub_types.all()}
            for i, product in enumerate(products):
                if product not in existing:
                    FertilizerSubType.objects.create(
                        fertilizer_type=ft, name=product, sort_order=i, is_active=True,
                    )
        sync_fertilizer_lookups_from_types()
        self.stdout.write(self.style.SUCCESS(f'Fertilizer types ready ({created} new types); lookups synced.'))
