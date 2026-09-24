"""Shared queryset filters for list/report endpoints."""


def apply_date_range(qs, request, date_field):
    date_from = request.query_params.get('date_from')
    if date_from:
        qs = qs.filter(**{f'{date_field}__gte': date_from})
    date_to = request.query_params.get('date_to')
    if date_to:
        qs = qs.filter(**{f'{date_field}__lte': date_to})
    return qs


def apply_exact(qs, request, param, field=None):
    value = request.query_params.get(param)
    if value:
        qs = qs.filter(**{field or param: value})
    return qs


def apply_icontains(qs, request, param, field=None):
    value = request.query_params.get(param)
    if value:
        qs = qs.filter(**{f'{field or param}__icontains': value})
    return qs
