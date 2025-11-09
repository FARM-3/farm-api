"""
Signals for production app to automatically log activities
when Harvests or Block objects are created, updated, or deleted.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Harvests, Block
from activities.models import Activity


@receiver(post_save, sender=Harvests)
def log_harvest_activity(sender, instance, created, **kwargs):
    """
    Log when a Harvest is created or updated.
    """
    if created:
        action = Activity.ACTION_CREATED
        object_repr = f"Harvest: {instance.weight_on_delivery}kg from {instance.worker_name}"
    else:
        action = Activity.ACTION_UPDATED
        object_repr = f"Harvest: {instance.weight_on_delivery}kg from {instance.worker_name}"

    content_type = ContentType.objects.get_for_model(Harvests)
    Activity.objects.create(
        user=None,  # Will be populated from request context if available
        action=action,
        content_type=content_type,
        object_id=instance.harvest_id,
        object_repr=object_repr,
    )


@receiver(post_save, sender=Block)
def log_block_activity(sender, instance, created, **kwargs):
    """
    Log when a Block is created or updated.
    """
    if created:
        action = Activity.ACTION_CREATED
        object_repr = f"Block: {instance.block_id}"
    else:
        action = Activity.ACTION_UPDATED
        object_repr = f"Block: {instance.block_id}"

    content_type = ContentType.objects.get_for_model(Block)
    Activity.objects.create(
        user=None,  # Will be populated from request context if available
        action=action,
        content_type=content_type,
        object_id=instance.block_id,
        object_repr=object_repr,
    )


@receiver(post_delete, sender=Harvests)
def log_harvest_deletion(sender, instance, **kwargs):
    """
    Log when a Harvest is deleted.
    """
    object_repr = f"Harvest: {instance.weight_on_delivery}kg from {instance.worker_name}"
    content_type = ContentType.objects.get_for_model(Harvests)
    Activity.objects.create(
        user=None,
        action=Activity.ACTION_DELETED,
        content_type=content_type,
        object_id=instance.harvest_id,
        object_repr=object_repr,
    )


@receiver(post_delete, sender=Block)
def log_block_deletion(sender, instance, **kwargs):
    """
    Log when a Block is deleted.
    """
    object_repr = f"Block: {instance.block_id}"
    content_type = ContentType.objects.get_for_model(Block)
    Activity.objects.create(
        user=None,
        action=Activity.ACTION_DELETED,
        content_type=content_type,
        object_id=instance.block_id,
        object_repr=object_repr,
    )
