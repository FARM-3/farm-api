"""Export ops helpers — QR codes, inventory sync, dossier enrichment."""
from decimal import Decimal

from processing.models import Bagging


def standard_lot_qr(lot_id: str, bagging_id=None) -> str:
    """Standard scan payload: LOT:{lot_id}"""
    lot_id = (lot_id or '').strip()
    if not lot_id:
        return ''
    if lot_id.upper().startswith('LOT:') or lot_id.upper().startswith('BAG:'):
        return lot_id
    return f'LOT:{lot_id}'


def resolve_lot_metadata(lot_id: str) -> dict:
    """Harvest, grade, coffee type from trace chain."""
    from processing.trace_service import trace_by_code

    lot_id = (lot_id or '').strip()
    trace = trace_by_code(f'LOT:{lot_id}') or trace_by_code(lot_id)
    meta = {
        'source_harvest_id': '',
        'coffee_type': '',
        'grade': '',
        'qr_code': standard_lot_qr(lot_id),
    }
    if not trace:
        return meta

    source = trace.get('source') or {}
    meta['source_harvest_id'] = trace.get('harvest_id') or ''
    meta['coffee_type'] = source.get('coffee_type') or ''
    grades = (trace.get('lineage') or {}).get('grades') or []
    if grades:
        meta['grade'] = grades[0].get('grade') or ''
    return meta


def sync_inventory_from_bagging(bagging: Bagging) -> None:
    """Create or update inventory lot when bagging is saved."""
    from .models import InventoryLot, Warehouse

    lot_id = (bagging.lot_id or '').strip()
    if not lot_id:
        return

    meta = resolve_lot_metadata(lot_id)
    warehouse = Warehouse.objects.filter(is_active=True).order_by('code').first()

    existing = InventoryLot.objects.filter(lot_id=lot_id).first()
    add_kg = Decimal(str(bagging.weight or 0))
    add_bags = bagging.no_of_bags or 0

    if existing and existing.status not in ('in_stock', 'reserved'):
        existing.notes = (existing.notes or '') + f'\nAdditional bagging +{add_kg}kg'
        existing.save(update_fields=['notes', 'updated_at'])
        return

    if existing:
        existing.total_kg = (existing.total_kg or 0) + add_kg
        existing.bags = (existing.bags or 0) + add_bags
        existing.moisture_pct = bagging.moisture_content
        if meta['coffee_type']:
            existing.coffee_type = meta['coffee_type']
        if meta['grade']:
            existing.grade = meta['grade']
        if meta['source_harvest_id']:
            existing.source_harvest_id = meta['source_harvest_id']
        existing.qr_code = bagging.qr_code or meta['qr_code']
        existing.save()
        return

    InventoryLot.objects.create(
        lot_id=lot_id,
        total_kg=add_kg,
        bags=add_bags,
        moisture_pct=bagging.moisture_content,
        coffee_type=meta['coffee_type'],
        grade=meta['grade'],
        source_harvest_id=meta['source_harvest_id'],
        qr_code=bagging.qr_code or meta['qr_code'],
        warehouse=warehouse,
        status='in_stock',
    )


def build_mass_balance(harvest_id: str) -> dict:
    """Mass balance for EUDR-style dossier (prototype)."""
    from processing.trace_service import trace_harvest

    trace = trace_harvest(harvest_id)
    if not trace:
        return {}
    source = trace.get('source') or {}
    loss = trace.get('loss_summary') or {}
    input_kg = source.get('harvest_weight') or loss.get('input_kg')
    output_kg = loss.get('output_kg')
    balance_ok = None
    if input_kg and output_kg:
        try:
            balance_ok = float(output_kg) <= float(input_kg)
        except (TypeError, ValueError):
            balance_ok = None
    return {
        'harvest_id': harvest_id,
        'input_kg': input_kg,
        'output_kg': output_kg,
        'overall_loss_pct': loss.get('overall_loss_pct'),
        'stages': loss.get('stages') or [],
        'balance_ok': balance_ok,
        'note': 'Prototype mass balance — not a certified EUDR submission.',
    }


def build_eudr_dossier(harvest_id: str) -> dict:
    """Enhanced due-diligence pack (prototype — no EU DDS integration)."""
    from processing.trace_service import trace_harvest
    from .models import ExportComplianceDocument

    trace = trace_harvest(harvest_id)
    if not trace:
        return None

    source = trace.get('source') or {}
    # Strip non-serializable farmer model before JSON/PDF export
    if isinstance(source.get('farmer_registration'), object) and hasattr(source['farmer_registration'], 'farmer_id'):
        fr = source['farmer_registration']
        source = {
            **source,
            'farmer_registration': {
                'farmer_id': fr.farmer_id,
                'gps_coordinates': fr.gps_coordinates,
                'village': fr.village,
                'parish': fr.parish,
                'district': fr.district,
            },
        }
    documents = list(
        ExportComplianceDocument.objects.filter(harvest_id=harvest_id).values(
            'id', 'document_type', 'title', 'notes', 'file', 'uploaded_at',
        )
    )

    return {
        'harvest_id': harvest_id,
        'generated_at': trace.get('quality_control_date'),
        'supplier': {
            'name': trace.get('farmer_name'),
            'type': source.get('source_type'),
            'location': source.get('location'),
            'gps': source.get('gps_coordinates'),
            'coffee_type': source.get('coffee_type'),
        },
        'intake': {
            'weight_kg': source.get('harvest_weight'),
            'date': source.get('delivery_date'),
        },
        'chain_of_custody': trace.get('stages') or [],
        'field_history': trace.get('field_history') or {},
        'lineage': trace.get('lineage') or {},
        'mass_balance': build_mass_balance(harvest_id),
        'documents': documents,
        'compliance_status': 'prototype',
        'disclaimer': (
            'Prototype export due-diligence pack. Includes GPS point, chain of custody, '
            'and mass balance. Does not constitute certified EUDR compliance or EU DDS submission.'
        ),
    }
