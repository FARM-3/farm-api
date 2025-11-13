from django.core.management.base import BaseCommand
from production.models import Harvests
from financialmanagement.models import Expense
from decimal import Decimal


class Command(BaseCommand):
    help = 'Sync all existing production harvests to expenses table'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without actually creating expenses',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Get all production harvests
        harvests = Harvests.objects.all()
        self.stdout.write(f"Found {harvests.count()} production harvests")

        created_count = 0
        skipped_count = 0

        for harvest in harvests:
            # Check if expense already exists for this harvest
            expense_exists = Expense.objects.filter(
                expense_name=f"Production - {harvest.worker_name}",
                date=harvest.date_of_delivery
            ).exists()

            if expense_exists:
                self.stdout.write(
                    self.style.WARNING(
                        f"SKIP: Expense already exists for {harvest.worker_name} on {harvest.date_of_delivery}"
                    )
                )
                skipped_count += 1
                continue

            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"WOULD CREATE: Production - {harvest.worker_name} "
                        f"(Amount: {harvest.amount_paid}, Date: {harvest.date_of_delivery})"
                    )
                )
            else:
                try:
                    Expense.objects.create(
                        expense_name=f"Production - {harvest.worker_name}",
                        category="Feed/Seed",
                        item="Coffee",
                        supplier=harvest.worker_name,
                        description=f"Production harvest: {harvest.weight_on_delivery}kg from block {harvest.block_id}",
                        amount=Decimal(str(harvest.amount_paid)) if harvest.amount_paid else Decimal('0.00'),
                        date=harvest.date_of_delivery,
                        location=harvest.block_id or "Farm"
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"CREATED: Production - {harvest.worker_name} "
                            f"(Amount: {harvest.amount_paid}, Date: {harvest.date_of_delivery})"
                        )
                    )
                    created_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"ERROR creating expense for {harvest.worker_name}: {str(e)}"
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
