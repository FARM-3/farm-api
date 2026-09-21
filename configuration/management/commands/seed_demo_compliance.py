"""Seed demo compliance documents and a completed GAP training session."""

from datetime import date, timedelta
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from configuration.models import FarmDocument, TrainingRecord

SEED_DIR = Path(__file__).resolve().parent.parent.parent / 'seed_files'

DOCUMENTS = [
    {
        'doc_id': 'DOC-EXPORT-001',
        'title': 'Coffee Export Licence',
        'doc_type': 'license',
        'issuer': 'Uganda Coffee Development Authority (UCDA)',
        'reference_no': 'UCDA-EXP-2025-8842',
        'issue_date': date(2025, 1, 15),
        'expiry_date': date(2026, 12, 31),
        'status': 'active',
        'notes': 'Valid for Arabica and Robusta green coffee exports.',
        'seed_file': 'export_licence.pdf',
    },
    {
        'doc_id': 'DOC-URA-001',
        'title': 'URA Tax Clearance Certificate',
        'doc_type': 'certificate',
        'issuer': 'Uganda Revenue Authority',
        'reference_no': 'URA-TC-2025-4410',
        'issue_date': date(2025, 3, 1),
        'expiry_date': date(2026, 2, 28),
        'status': 'active',
        'notes': 'Annual tax compliance certificate for agribusiness operations.',
        'seed_file': 'ura_certificate.pdf',
    },
    {
        'doc_id': 'DOC-ORG-001',
        'title': 'Organic Certification',
        'doc_type': 'certificate',
        'issuer': 'Certified Organic Uganda',
        'reference_no': 'COU-ORG-2024-1198',
        'issue_date': date(2024, 6, 1),
        'expiry_date': date(2025, 5, 31),
        'status': 'active',
        'notes': 'EU-equivalent organic standard for washed Arabica.',
        'seed_file': 'organic_certificate.pdf',
    },
]

TRAINING = {
    'training_id': 'TRN-GAP-001',
    'title': 'Good Agricultural Practices (GAP) — Farmer Outgrowers',
    'topic': 'GAP, record keeping, cherry quality at collection',
    'trainer': 'Extension Officer — START Facility',
    'location': 'Mbale Aggregation Centre',
    'start_date': date.today() - timedelta(days=14),
    'end_date': date.today() - timedelta(days=14),
    'attendees': 42,
    'status': 'completed',
    'notes': 'Completed session for outgrower farmers ahead of main harvest season.',
}


def _minimal_pdf(title: str) -> bytes:
    """Minimal valid PDF with a title line for demo preview."""
    content = f"""BT /F1 18 Tf 72 720 Td ({title}) Tj ET"""
    stream = f"4 0 obj<</Length {len(content)}>>stream\n{content}\nendstream"
    body = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
{stream}
5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000052 00000 n
0000000101 00000 n
0000000212 00000 n
0000000300 00000 n
trailer<</Size 6/Root 1 0 R>>
startxref
380
%%EOF"""
    return body.encode('latin-1')


class Command(BaseCommand):
    help = 'Seed demo compliance documents (with files) and a completed GAP training'

    def handle(self, *args, **options):
        SEED_DIR.mkdir(parents=True, exist_ok=True)
        doc_count = 0

        for spec in DOCUMENTS:
            doc, created = FarmDocument.objects.get_or_create(
                doc_id=spec['doc_id'],
                defaults={k: v for k, v in spec.items() if k != 'seed_file'},
            )
            seed_path = SEED_DIR / spec['seed_file']
            if not seed_path.exists():
                seed_path.write_bytes(_minimal_pdf(spec['title']))

            if created or not doc.file:
                with seed_path.open('rb') as fh:
                    doc.file.save(spec['seed_file'], ContentFile(fh.read()), save=True)
                doc_count += 1
                self.stdout.write(f'  document: {spec["title"]}')
            else:
                self.stdout.write(f'  skip document: {spec["title"]} (exists)')

        trn, created = TrainingRecord.objects.get_or_create(
            training_id=TRAINING['training_id'],
            defaults=TRAINING,
        )
        if created:
            self.stdout.write(f'  training: {TRAINING["title"]}')
        else:
            self.stdout.write(f'  skip training: {TRAINING["title"]} (exists)')

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {doc_count} document(s) and {"1" if created else "0"} training record'
        ))
