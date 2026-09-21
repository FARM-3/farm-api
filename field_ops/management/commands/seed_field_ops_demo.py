"""Seed demo block activities and surveillance reports for trace/demo."""

from datetime import date, timedelta

from django.core.management.base import BaseCommand

from field_ops.models import BlockActivityLog, SurveillanceReport

BLOCK = 'B01'


class Command(BaseCommand):
    help = 'Seed demo block activity logs and surveillance reports'

    def handle(self, *args, **options):
        activities = [
            {
                'log_id': 'BAL-DEMO-001',
                'block_id': BLOCK,
                'log_type': 'practice',
                'title': 'Pruning — shade management',
                'practices': ['Pruning', 'Shade management'],
                'activity_date': date.today() - timedelta(days=45),
                'weather_conditions': ['sunny'],
                'reported_by_name': 'Block Champion',
                'notes': 'Removed dead wood; improved canopy light penetration.',
            },
            {
                'log_id': 'BAL-DEMO-002',
                'block_id': BLOCK,
                'log_type': 'input',
                'title': 'NPK fertilizer application',
                'input_type': 'fertilizer',
                'input_name': 'NPK 17-17-17',
                'quantity': 25,
                'unit': 'kg',
                'activity_date': date.today() - timedelta(days=30),
                'weather_conditions': ['cloudy'],
                'reported_by_name': 'Extension Officer',
                'notes': 'Applied around root zone after soil moisture check.',
            },
            {
                'log_id': 'BAL-DEMO-003',
                'block_id': BLOCK,
                'log_type': 'input',
                'title': 'Copper-based spray — CBD prevention',
                'input_type': 'pesticide',
                'input_name': 'Copper oxychloride',
                'quantity': 2,
                'unit': 'L',
                'activity_date': date.today() - timedelta(days=14),
                'weather_conditions': ['sunny', 'windy'],
                'reported_by_name': 'Block Champion',
                'harvest_id': 'FH-DEMO001',
                'notes': 'Preventive spray before main harvest window.',
            },
            {
                'log_id': 'BAL-DEMO-004',
                'block_id': BLOCK,
                'log_type': 'practice',
                'title': 'Mulching under mature trees',
                'practices': ['Mulching', 'Agro-forestry'],
                'activity_date': date.today() - timedelta(days=7),
                'weather_conditions': ['rainy'],
                'reported_by_name': 'Block Champion',
            },
        ]

        created_a = 0
        for spec in activities:
            _, created = BlockActivityLog.objects.get_or_create(
                log_id=spec['log_id'],
                defaults=spec,
            )
            if created:
                created_a += 1
                self.stdout.write(f'  activity: {spec["title"]}')

        reports = [
            {
                'report_id': 'SUR-DEMO-001',
                'block_id': BLOCK,
                'title': 'Leaf rust spots on lower canopy',
                'description': 'Orange spots observed on 15–20 trees in south-east corner. Recommend follow-up spray.',
                'severity': 'medium',
                'issue_type': 'disease',
                'weather_conditions': ['humid', 'cloudy'],
                'location': f'{BLOCK} — south-east section',
                'reported_by_name': 'Block Champion',
                'status': 'open',
            },
            {
                'report_id': 'SUR-DEMO-002',
                'block_id': BLOCK,
                'title': 'Cherry ripeness uneven — Block 01',
                'description': 'Mixed red and green cherry on same branches; may affect float test grade.',
                'severity': 'low',
                'issue_type': 'quality',
                'weather_conditions': ['sunny'],
                'location': f'{BLOCK}',
                'reported_by_name': 'QC Officer',
                'status': 'in_review',
            },
        ]

        created_s = 0
        for spec in reports:
            _, created = SurveillanceReport.objects.get_or_create(
                report_id=spec['report_id'],
                defaults=spec,
            )
            if created:
                created_s += 1
                self.stdout.write(f'  surveillance: {spec["title"]}')

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {created_a} block activities and {created_s} surveillance reports'
        ))
