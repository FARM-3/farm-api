"""
Harvest traceability service — walks existing records by ID convention.
"""
from aggregation.models import FarmerHarvest, FarmerRegistration
from production.models import Harvests

from .models import (
    Bagging,
    Drying,
    Fermenting,
    Floating,
    Hulling,
    NaturalSundrying,
    Ripeness,
    Washing,
)


def _float(val):
    if val is None:
        return None
    return float(val)


def _grade_ids_for_harvest(harvest_id):
    return list(
        Floating.objects.filter(harvest=harvest_id).values_list('grade_id', flat=True)
    )


def _processes_containing_grade(model, grade_id):
    matches = []
    for record in model.objects.all():
        ids = record.grade_ids if isinstance(record.grade_ids, list) else []
        if grade_id in ids:
            matches.append(record)
    return matches


def _resolve_harvest_source(harvest_id):
    """Return source metadata from production or aggregation harvest."""
    try:
        fh = FarmerHarvest.objects.get(harvest_id=harvest_id)
        gps = fh.gps_coordinates_delivery
        location = fh.location_of_delivery
        farmer_reg = None
        try:
            parts = (fh.name or '').strip().split(' ', 1)
            if len(parts) == 2:
                farmer_reg = FarmerRegistration.objects.filter(
                    first_name=parts[0], last_name=parts[1]
                ).first()
            if not farmer_reg:
                farmer_reg = FarmerRegistration.objects.filter(
                    first_name__iexact=fh.name.split()[0] if fh.name else ''
                ).first()
        except Exception:
            farmer_reg = None

        if farmer_reg and farmer_reg.gps_coordinates:
            gps = gps or farmer_reg.gps_coordinates
            location = location or f"{farmer_reg.village}, {farmer_reg.parish}, {farmer_reg.district}"

        return {
            'source_type': 'aggregation',
            'farmer_name': fh.name,
            'block_id': None,
            'harvest_weight': _float(fh.weight_on_delivery),
            'delivery_date': fh.date_of_delivery.isoformat() if fh.date_of_delivery else None,
            'location': location,
            'gps_coordinates': gps,
            'coffee_type': fh.coffee_type,
            'amount_paid': _float(fh.amount_paid),
        }
    except FarmerHarvest.DoesNotExist:
        pass

    try:
        h = Harvests.objects.get(harvest_id=harvest_id)
        return {
            'source_type': 'estate',
            'farmer_name': h.worker_name,
            'block_id': h.block_id,
            'harvest_weight': _float(h.weight_on_delivery),
            'delivery_date': h.date_of_delivery.isoformat() if h.date_of_delivery else None,
            'location': h.block_id,
            'gps_coordinates': None,
            'coffee_type': 'Arabica',
        }
    except Harvests.DoesNotExist:
        return None


def _stage_status(completed, in_progress=False):
    if completed:
        return 'completed'
    if in_progress:
        return 'in_progress'
    return 'pending'


def _build_loss_summary(harvest_weight, floating_records, drying_records, bagging_records):
    """Build weight loss chain from existing field data."""
    stages = []
    prev_weight = harvest_weight

    if floating_records:
        total_floating = sum(_float(r.weight) or 0 for r in floating_records)
        if total_floating:
            loss_pct = None
            if prev_weight and prev_weight > 0:
                loss_pct = round((1 - total_floating / prev_weight) * 100, 1)
            stages.append({
                'stage': 'Quality Control (Floating)',
                'input_kg': prev_weight,
                'output_kg': total_floating,
                'loss_pct': loss_pct,
            })
            prev_weight = total_floating

    if drying_records:
        ordered = sorted(drying_records, key=lambda r: r.date)
        first_w = _float(ordered[0].weight_before or ordered[0].weight)
        last_w = _float(ordered[-1].weight)
        if first_w and last_w:
            loss_pct = round((1 - last_w / first_w) * 100, 1) if first_w > 0 else None
            stages.append({
                'stage': 'Drying',
                'input_kg': first_w,
                'output_kg': last_w,
                'loss_pct': loss_pct,
                'outturn': _float(ordered[-1].outturn),
            })
            prev_weight = last_w

    if bagging_records:
        total_bagged = sum(_float(r.weight) or 0 for r in bagging_records)
        if total_bagged:
            loss_pct = None
            if prev_weight and prev_weight > 0:
                loss_pct = round((1 - total_bagged / prev_weight) * 100, 1)
            stages.append({
                'stage': 'Bagging',
                'input_kg': prev_weight,
                'output_kg': total_bagged,
                'loss_pct': loss_pct,
                'bags': sum(r.no_of_bags for r in bagging_records),
            })

    overall_loss = None
    if harvest_weight and bagging_records:
        total_out = sum(_float(r.weight) or 0 for r in bagging_records)
        if harvest_weight > 0 and total_out:
            overall_loss = round((1 - total_out / harvest_weight) * 100, 1)

    return {
        'stages': stages,
        'overall_loss_pct': overall_loss,
        'input_kg': harvest_weight,
        'output_kg': sum(_float(r.weight) or 0 for r in bagging_records) if bagging_records else None,
    }


def _serialize_block_activity(log):
    return {
        'log_id': log.log_id,
        'block_id': log.block_id,
        'log_type': log.log_type,
        'title': log.title,
        'description': log.description,
        'practices': log.practices or [],
        'input_type': log.input_type,
        'input_name': log.input_name,
        'quantity': _float(log.quantity),
        'unit': log.unit,
        'activity_date': log.activity_date.isoformat() if log.activity_date else None,
        'weather_conditions': log.weather_conditions or [],
        'reported_by': log.reported_by_name,
        'notes': log.notes,
    }


def _serialize_surveillance(report):
    return {
        'report_id': report.report_id,
        'block_id': report.block_id,
        'title': report.title,
        'description': report.description,
        'severity': report.severity,
        'issue_type': report.issue_type,
        'status': report.status,
        'weather_conditions': report.weather_conditions or [],
        'location': report.location,
        'reported_by': report.reported_by_name,
        'created_at': report.created_at.isoformat() if report.created_at else None,
    }


def _field_history_for_block(block_id, before_date=None):
    """Block-level practices, inputs, and surveillance for trace reports."""
    try:
        from field_ops.models import BlockActivityLog, SurveillanceReport
    except ImportError:
        return {'block_activities': [], 'surveillance_reports': []}

    if not block_id:
        return {'block_activities': [], 'surveillance_reports': []}

    activities = BlockActivityLog.objects.filter(block_id=block_id).order_by('-activity_date')
    surveillance = SurveillanceReport.objects.filter(block_id=block_id).order_by('-created_at')
    if before_date:
        activities = activities.filter(activity_date__lte=before_date)
        surveillance = surveillance.filter(created_at__date__lte=before_date)

    return {
        'block_id': block_id,
        'block_activities': [_serialize_block_activity(a) for a in activities[:50]],
        'surveillance_reports': [_serialize_surveillance(s) for s in surveillance[:20]],
        'inputs_summary': [
            {
                'date': a.activity_date.isoformat(),
                'input': a.input_name,
                'type': a.input_type,
                'quantity': _float(a.quantity),
                'unit': a.unit,
            }
            for a in activities.filter(log_type='input').order_by('-activity_date')[:20]
        ],
        'practices_summary': [
            {
                'date': a.activity_date.isoformat(),
                'practices': a.practices or [],
                'title': a.title,
            }
            for a in activities.filter(log_type='practice').order_by('-activity_date')[:20]
        ],
    }


def trace_harvest(harvest_id):
    """
    Build full trace payload for a harvest_id.
    Returns dict or None if harvest not found anywhere.
    """
    source = _resolve_harvest_source(harvest_id)
    if not source:
        # Allow tracing processing-only records
        source = {
            'source_type': 'unknown',
            'farmer_name': 'Unknown',
            'harvest_weight': None,
        }

    ripeness = Ripeness.objects.filter(harvest=harvest_id).first()
    floating_records = list(Floating.objects.filter(harvest=harvest_id).order_by('date'))
    grade_ids = [r.grade_id for r in floating_records]

    processing_steps = []
    for gid in grade_ids:
        for rec in _processes_containing_grade(Fermenting, gid):
            processing_steps.append({'type': 'fermenting', 'id': rec.processing_id, 'weight': _float(rec.weight), 'date': str(rec.end_date)})
        for rec in _processes_containing_grade(Washing, gid):
            processing_steps.append({'type': 'washing', 'id': rec.processing_id, 'weight': _float(rec.weight), 'date': str(rec.date)})
        for rec in _processes_containing_grade(NaturalSundrying, gid):
            processing_steps.append({'type': 'natural_sundrying', 'id': rec.processing_id, 'weight': _float(rec.weight), 'date': str(rec.start_date)})

    processing_ids = {s['id'] for s in processing_steps if s.get('id')}
    drying_records = list(
        Drying.objects.filter(processing_id__in=processing_ids).order_by('date')
    ) if processing_ids else []

    # Also link drying by harvest prefix in processing_id if present
    if not drying_records:
        drying_records = list(
            Drying.objects.filter(processing_id__icontains=harvest_id[:6]).order_by('date')
        )

    lot_ids = list({r.lot_id for r in drying_records if r.lot_id})
    hulling_records = list(
        Hulling.objects.filter(lot_id__in=lot_ids).order_by('-date')
    ) if lot_ids else []
    bagging_records = list(
        Bagging.objects.filter(lot_id__in=lot_ids).order_by('-date')
    ) if lot_ids else []

    # Stage timeline for UI
    qc_done = bool(ripeness or floating_records)
    qc_date = None
    if floating_records:
        qc_date = floating_records[0].date.isoformat()
    elif ripeness:
        qc_date = ripeness.date.isoformat()

    proc_done = bool(processing_steps)
    proc_date = processing_steps[0]['date'] if processing_steps else None

    drying_done = bool(drying_records)
    drying_in_progress = drying_done and not bagging_records
    drying_date = drying_records[-1].date.isoformat() if drying_records else None

    hulling_done = bool(hulling_records)
    hulling_date = hulling_records[0].date.isoformat() if hulling_records else None

    bagging_done = bool(bagging_records)
    bagging_date = bagging_records[0].date.date().isoformat() if bagging_records else None

    stages = [
        {'name': 'Quality Control', 'status': _stage_status(qc_done), 'date': qc_date},
        {'name': 'Processing Type Selection', 'status': _stage_status(proc_done), 'date': proc_date},
        {'name': 'Drying', 'status': _stage_status(drying_done, drying_in_progress), 'date': drying_date},
        {'name': 'Hulling', 'status': _stage_status(hulling_done), 'date': hulling_date},
        {'name': 'Bagging', 'status': _stage_status(bagging_done), 'date': bagging_date},
    ]

    current_stage = 'Not Started'
    for stage in reversed(stages):
        if stage['status'] == 'in_progress':
            current_stage = stage['name']
            break
    if current_stage == 'Not Started':
        for stage in reversed(stages):
            if stage['status'] == 'completed':
                current_stage = stage['name']
                break

    loss_summary = _build_loss_summary(
        source.get('harvest_weight'),
        floating_records,
        drying_records,
        bagging_records,
    )

    lineage = {
        'harvest_id': harvest_id,
        'grades': [
            {'grade_id': r.grade_id, 'grade': r.grade, 'weight_kg': _float(r.weight)}
            for r in floating_records
        ],
        'processing_steps': processing_steps,
        'lot_ids': lot_ids,
        'hulling': [
            {
                'lot_id': h.lot_id,
                'weight_before_kg': _float(h.weight_before),
                'weight_after_kg': _float(h.weight_after),
                'outturn': _float(h.outturn),
                'screen_size': h.screen_size,
                'date': h.date.isoformat() if h.date else None,
            }
            for h in hulling_records
        ],
        'bagging': [
            {
                'lot_id': b.lot_id,
                'weight_kg': _float(b.weight),
                'bags': b.no_of_bags,
                'moisture': _float(b.moisture_content),
                'qr_code': b.qr_code,
                'date': b.date.isoformat() if b.date else None,
            }
            for b in bagging_records
        ],
    }

    delivery_date = source.get('delivery_date')
    before_date = None
    if delivery_date:
        try:
            from datetime import date
            before_date = date.fromisoformat(delivery_date[:10])
        except (ValueError, TypeError):
            before_date = None

    block_id = source.get('block_id')
    field_history = _field_history_for_block(block_id, before_date=before_date)

    return {
        'harvest_id': harvest_id,
        'farmer_name': source.get('farmer_name', 'Unknown'),
        'source_type': source.get('source_type'),
        'field_history': field_history,
        'current_stage': current_stage,
        'stages': stages,
        'quality_control_completed': qc_done,
        'quality_control_date': qc_date,
        'processing_type_selected': proc_done,
        'processing_type_date': proc_date,
        'drying_completed': drying_done and not drying_in_progress,
        'drying_started': drying_done,
        'drying_date': drying_date,
        'hulling_completed': hulling_done,
        'hulling_date': hulling_date,
        'bagging_completed': bagging_done,
        'bagging_date': bagging_date,
        'loss_summary': loss_summary,
        'lineage': lineage,
        'source': source,
        'ripeness_score': _float(ripeness.ripeness_score) if ripeness else None,
    }


def trace_by_code(code):
    """Resolve LOT: or BAG: or raw lot_id / harvest_id codes."""
    if not code:
        return None

    normalized = code.strip()
    if normalized.upper().startswith('LOT:'):
        lot_id = normalized.split(':', 1)[1].strip()
        drying = Drying.objects.filter(lot_id=lot_id).order_by('-date').first()
        if drying and drying.processing_id:
            proc_id = drying.processing_id
            for model in (Washing, Fermenting, NaturalSundrying):
                for rec in model.objects.all():
                    if proc_id == rec.processing_id or proc_id.startswith(rec.processing_id.split('-')[0]):
                        grade_ids = rec.grade_ids if isinstance(rec.grade_ids, list) else []
                        for gid in grade_ids:
                            fl = Floating.objects.filter(grade_id=gid).first()
                            if fl:
                                return trace_harvest(fl.harvest)
            prefix = proc_id.replace('-WSH', '').replace('-FER', '').replace('-SUN', '')
            if prefix:
                result = trace_harvest(prefix)
                if result:
                    return result
        bagging = Bagging.objects.filter(lot_id=lot_id).first()
        if bagging:
            return {
                'lot_id': lot_id,
                'bagging': list(Bagging.objects.filter(lot_id=lot_id).values()),
                'note': 'Partial trace — link harvest via lot processing_id when drying records exist.',
            }
        return None

    if normalized.upper().startswith('BAG:'):
        parts = normalized.split(':')
        lot_id = parts[1] if len(parts) > 1 else None
        if lot_id:
            return trace_by_code(f'LOT:{lot_id}')

    # Direct harvest_id lookup
    result = trace_harvest(normalized)
    if result:
        return result

    # Try lot_id direct
    bagging = Bagging.objects.filter(lot_id=normalized).first()
    if bagging:
        return trace_by_code(f'LOT:{normalized}')

    return None
