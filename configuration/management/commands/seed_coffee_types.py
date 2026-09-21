from django.core.management.base import BaseCommand
from configuration.models import CoffeeType, CoffeeSubType

DEFAULTS = {
    'Arabica': ['SL14', 'SL28', 'KP423', 'Nyasaland'],
    'Robusta': ['KR-01', 'KR-02', 'KR-03', 'Screen 18', 'Screen 15'],
    'Liberica': ['LIB-01'],
}


class Command(BaseCommand):
    help = 'Seed coffee types with sub-types'

    def handle(self, *args, **options):
        for name, subs in DEFAULTS.items():
            ct, _ = CoffeeType.objects.get_or_create(name=name, defaults={'is_active': True})
            if ct.sub_types.exists():
                continue
            for i, sub in enumerate(subs):
                CoffeeSubType.objects.create(coffee_type=ct, name=sub, code=sub, sort_order=i)
        self.stdout.write(self.style.SUCCESS('Coffee types seeded'))
