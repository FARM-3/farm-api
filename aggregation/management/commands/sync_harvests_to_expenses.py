from django.core.management.base import BaseCommand
from aggregation.models import FarmerHarvest
from financialmanagement.models import Expense
from decimal import Decimal


class Command(BaseCommand):
    help = 'Sync all existing farmer harvests to expenses table'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without actually creating expenses',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Get all farmer harvests
        harvests = FarmerHarvest.objects.all()
        self.stdout.write(f"Found {harvests.count()} farmer harvests")

        created_count = 0
        skipped_count = 0

        for harvest in harvests:
            # Check if expense already exists for this harvest
            expense_exists = Expense.objects.filter(
                expense_name=f"Aggregation - {harvest.name}",
                date=harvest.date_of_delivery
            ).exists()

            if expense_exists:
                self.stdout.write(
                    self.style.WARNING(
                        f"SKIP: Expense already exists for {harvest.name} on {harvest.date_of_delivery}"
                    )
                )
                skipped_count += 1
                continue

            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"WOULD CREATE: Aggregation - {harvest.name} "
                        f"(Amount: {harvest.amount_paid}, Date: {harvest.date_of_delivery})"
                    )
                )
            else:
                try:
                    Expense.objects.create(
                        expense_name=f"Aggregation - {harvest.name}",
                        category="Feed/Seed",
                        item=harvest.coffee_type or "Coffee",
                        supplier=harvest.name,
                        description=f"{harvest.weight_on_delivery}kg of {harvest.coffee_type or 'coffee'} from {harvest.name}",
                        amount=Decimal(str(harvest.amount_paid)) if harvest.amount_paid else Decimal('0.00'),
                        date=harvest.date_of_delivery,
                        location=harvest.location_of_delivery or "Farm"
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"CREATED: Aggregation - {harvest.name} "
                            f"(Amount: {harvest.amount_paid}, Date: {harvest.date_of_delivery})"
                        )
                    )
                    created_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"ERROR creating expense for {harvest.name}: {str(e)}"
                        )
                    )

        # Summary
        self.stdout.write("\n" + "="*60)
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"DRY RUN - Would create {created_count} expenses"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Created {created_count} expenses"))
        self.stdout.write(f"Skipped {skipped_count} (already existed)")
        self.stdout.write("="*60)
