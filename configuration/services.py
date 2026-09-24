"""Sync helpers so nested config models stay visible to flat lookup consumers."""

from .models import ConfigCategory, FertilizerType, LookupOption


def sync_fertilizer_lookups_from_types():
    """Mirror FertilizerSubType names into legacy LookupOption categories."""
    mapping = {
        'Organic': ConfigCategory.FERTILIZER_ORGANIC,
        'Inorganic': ConfigCategory.FERTILIZER_INORGANIC,
    }
    for ft in FertilizerType.objects.filter(is_active=True).prefetch_related('sub_types'):
        category = mapping.get(ft.name)
        if not category:
            continue
        products = list(
            ft.sub_types.filter(is_active=True).order_by('sort_order', 'name').values_list('name', flat=True)
        )
        LookupOption.objects.filter(category=category).delete()
        for idx, name in enumerate(products):
            LookupOption.objects.create(
                category=category,
                value=name,
                label=name,
                sort_order=idx,
                is_active=True,
            )


def apply_sale_item_rates(rates: dict):
    """Set default_rate/unit_label on sale_item lookup rows."""
    for name, (rate, unit) in rates.items():
        LookupOption.objects.filter(category=ConfigCategory.SALE_ITEM, value=name).update(
            default_rate=rate,
            unit_label=unit,
            is_active=True,
        )
