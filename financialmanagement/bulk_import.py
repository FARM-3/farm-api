"""CSV/Excel bulk import helpers for staff and wages."""

import csv
import io
from datetime import datetime
from django.http import HttpResponse
from .models import Staff, Wage


STAFF_TEMPLATE_HEADERS = [
    'first_name', 'last_name', 'gender', 'nin', 'district', 'sub_county',
    'parish', 'village', 'employment_type', 'monthly_salary', 'date_hired',
]

WAGE_TEMPLATE_HEADERS = [
    'employee_name', 'staff_id', 'days_missed', 'amount_paid', 'date_of_payment',
]


def download_template(entity_type):
    headers = STAFF_TEMPLATE_HEADERS if entity_type == 'staff' else WAGE_TEMPLATE_HEADERS
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{entity_type}_import_template.csv"'
    writer = csv.writer(response)
    writer.writerow(headers)
    if entity_type == 'staff':
        writer.writerow([
            'John', 'Okello', 'Male', 'CM1234567890123', 'Wakiso', 'Namayumba Sub-County',
            'Namayumba', 'Village A', 'Full Time', '500000', '2024-01-15',
        ])
    else:
        writer.writerow(['John Okello', 'RF001', '0', '450000', '2026-09-01'])
    return response


def parse_csv_upload(file):
    content = file.read().decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(content))
    return list(reader)


def import_staff_rows(rows):
    created, errors = 0, []
    for i, row in enumerate(rows, start=2):
        try:
            date_hired = row.get('date_hired') or datetime.now().date().isoformat()
            Staff.objects.create(
                first_name=row.get('first_name', '').strip(),
                last_name=row.get('last_name', '').strip(),
                gender=row.get('gender', 'Male'),
                nin=row.get('nin', '').strip().upper(),
                district=row.get('district', ''),
                sub_county=row.get('sub_county', ''),
                parish=row.get('parish', ''),
                village=row.get('village', ''),
                employment_type=row.get('employment_type', 'Full Time'),
                monthly_salary=int(row.get('monthly_salary') or 0),
                date_hired=date_hired,
            )
            created += 1
        except Exception as e:
            errors.append({'row': i, 'error': str(e)})
    return created, errors


def import_wage_rows(rows):
    created, errors = 0, []
    for i, row in enumerate(rows, start=2):
        try:
            staff = None
            staff_id = row.get('staff_id', '').strip()
            if staff_id:
                staff = Staff.objects.filter(staff_id=staff_id).first()
            Wage.objects.create(
                employee_name=row.get('employee_name', '').strip(),
                staff=staff,
                days_missed=int(row.get('days_missed') or 0),
                amount_paid=int(row.get('amount_paid') or 0),
                date_of_payment=row.get('date_of_payment') or datetime.now().date().isoformat(),
            )
            created += 1
        except Exception as e:
            errors.append({'row': i, 'error': str(e)})
    return created, errors
