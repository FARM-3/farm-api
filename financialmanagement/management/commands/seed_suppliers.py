from django.core.management.base import BaseCommand
from financialmanagement.models import Supplier


DEMO_SUPPLIERS = [
    dict(name='Agro Inputs Uganda Ltd', category='inputs', contact_person='James Okello', phone='0700111222', district='Kampala', address='Industrial Area, Kampala'),
    dict(name='Nakasero Fuel Station', category='transport', contact_person='Sarah N.', phone='0700333444', district='Kampala', address='Nakasero Road'),
    dict(name='Mukono Farm Tools', category='equipment', contact_person='Peter Ssemwanga', phone='0700555666', district='Mukono', address='Mukono Town'),
    dict(name='UCDA Extension Services', category='services', contact_person='Grace Nakato', phone='0700777888', district='Wakiso', notes='Training & certification support'),
    dict(name='Green Valley Organics', category='inputs', contact_person='David K.', phone='0700999000', district='Jinja', address='Compost & organic fertilizer supplier'),
]


class Command(BaseCommand):
    help = 'Seed demo suppliers for expenses and procurement'

    def handle(self, *args, **options):
        created = 0
        for row in DEMO_SUPPLIERS:
            _, was_created = Supplier.objects.get_or_create(
                name=row['name'],
                defaults=row,
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Suppliers ready ({created} new, {Supplier.objects.count()} total)'))
