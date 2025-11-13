"""
Signals for aggregation app to automatically log activities
when FarmerRegistration or FarmerHarvest objects are created, updated, or deleted.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import FarmerRegistration, FarmerHarvest
from activities.models import Activity


@receiver(post_save, sender=FarmerRegistration)
def log_farmer_activity(sender, instance, created, **kwargs):
    """
    Log when a FarmerRegistration is created or updated.
    """
    if created:
        action = Activity.ACTION_CREATED
        object_repr = f"Farmer: {instance.first_name} {instance.last_name}"
    else:
        action = Activity.ACTION_UPDATED
        object_repr = f"Farmer: {instance.first_name} {instance.last_name}"

    content_type = ContentType.objects.get_for_model(FarmerRegistration)
    Activity.objects.create(
        user=None,  # Will be populated from request context if available
        action=action,
        content_type=content_type,
        object_id=instance.id,
        object_repr=object_repr,
    )


@receiver(post_save, sender=FarmerHarvest)
def log_harvest_activity(sender, instance, created, **kwargs):
    """
    Log when a FarmerHarvest is created or updated.
    """
    if created:
        action = Activity.ACTION_CREATED
        object_repr = f"Harvest: {instance.weight_on_delivery}kg from {instance.name or 'Farmer'}"
    else:
        action = Activity.ACTION_UPDATED
        object_repr = f"Harvest: {instance.weight_on_delivery}kg from {instance.name or 'Farmer'}"

    content_type = ContentType.objects.get_for_model(FarmerHarvest)
    Activity.objects.create(
        user=None,  # Will be populated from request context if available
        action=action,
        content_type=content_type,
        object_id=instance.harvest_id,  # FIXED: Use harvest_id as primary key
        object_repr=object_repr,
    )


@receiver(post_delete, sender=FarmerRegistration)
def log_farmer_deletion(sender, instance, **kwargs):
    """
    Log when a FarmerRegistration is deleted.
    """
    object_repr = f"Farmer: {instance.first_name} {instance.last_name}"
    content_type = ContentType.objects.get_for_model(FarmerRegistration)
    Activity.objects.create(
        user=None,
        action=Activity.ACTION_DELETED,
        content_type=content_type,
        object_id=instance.id,
        object_repr=object_repr,
    )


@receiver(post_delete, sender=FarmerHarvest)
def log_harvest_deletion(sender, instance, **kwargs):
    """
    Log when a FarmerHarvest is deleted.
    """
    object_repr = f"Harvest: {instance.weight_on_delivery}kg from {instance.name or 'Farmer'}"
    content_type = ContentType.objects.get_for_model(FarmerHarvest)
    Activity.objects.create(
        user=None,
        action=Activity.ACTION_DELETED,
        content_type=content_type,
        object_id=instance.harvest_id,  # FIXED: Use harvest_id as primary key
        object_repr=object_repr,
    )
