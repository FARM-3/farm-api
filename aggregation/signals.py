"""
Signals for aggregation app to automatically log activities
when FarmerRegistration or FarmerHarvest objects are created, updated, or deleted.

Note: All signal handlers include try-except blocks to prevent signal errors
from breaking the main operation (create/update/delete). Activity logging
failures are logged but do not affect data integrity.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import FarmerRegistration, FarmerHarvest
from activities.models import Activity

logger = logging.getLogger(__name__)


@receiver(post_save, sender=FarmerRegistration)
def log_farmer_activity(sender, instance, created, **kwargs):
    """
    Log when a FarmerRegistration is created or updated.
    Signal failures are caught and logged but do not affect the main operation.
    """
    try:
        if created:
            action = Activity.ACTION_CREATED
            object_repr = f"Farmer: {instance.first_name} {instance.last_name}"
        else:
            action = Activity.ACTION_UPDATED
            object_repr = f"Farmer: {instance.first_name} {instance.last_name}"

        content_type = ContentType.objects.get_for_model(FarmerRegistration)
        Activity.objects.create(
            user=None,  # Activity allows null user for system-triggered operations
            action=action,
            content_type=content_type,
            object_id=instance.farmer_id,
            object_repr=object_repr,
        )
        logger.info(f"[aggregation.signals] Logged farmer {action}: {instance.farmer_id}")
    except Exception as e:
        logger.error(f"[aggregation.signals] Failed to log farmer activity for {instance.farmer_id}: {str(e)}", exc_info=True)
        # Note: We do NOT re-raise this exception - activity logging failure should not break the operation


@receiver(post_save, sender=FarmerHarvest)
def log_harvest_activity(sender, instance, created, **kwargs):
    """
    Log when a FarmerHarvest is created or updated.
    Signal failures are caught and logged but do not affect the main operation.
    """
    try:
        if created:
            action = Activity.ACTION_CREATED
            object_repr = f"Harvest: {instance.weight_on_delivery}kg from {instance.name or 'Farmer'}"
        else:
            action = Activity.ACTION_UPDATED
            object_repr = f"Harvest: {instance.weight_on_delivery}kg from {instance.name or 'Farmer'}"

        content_type = ContentType.objects.get_for_model(FarmerHarvest)
        Activity.objects.create(
            user=None,  # Activity allows null user for system-triggered operations
            action=action,
            content_type=content_type,
            object_id=instance.harvest_id,
            object_repr=object_repr,
        )
        logger.info(f"[aggregation.signals] Logged harvest {action}: {instance.harvest_id}")
    except Exception as e:
        logger.error(f"[aggregation.signals] Failed to log harvest activity for {instance.harvest_id}: {str(e)}", exc_info=True)
        # Note: We do NOT re-raise this exception - activity logging failure should not break the operation


@receiver(post_delete, sender=FarmerRegistration)
def log_farmer_deletion(sender, instance, **kwargs):
    """
    Log when a FarmerRegistration is deleted.
    Signal failures are caught and logged but do not affect the main operation.

    IMPORTANT: This runs AFTER deletion is complete and committed to the database.
    By wrapping in try-except, we ensure deletion succeeds even if logging fails.
    """
    try:
        object_repr = f"Farmer: {instance.first_name} {instance.last_name}"
        content_type = ContentType.objects.get_for_model(FarmerRegistration)
        Activity.objects.create(
            user=None,  # Activity allows null user for system-triggered operations
            action=Activity.ACTION_DELETED,
            content_type=content_type,
            object_id=instance.farmer_id,
            object_repr=object_repr,
        )
        logger.info(f"[aggregation.signals] Logged farmer deletion: {instance.farmer_id}")
    except Exception as e:
        logger.error(f"[aggregation.signals] Failed to log farmer deletion for {instance.farmer_id}: {str(e)}", exc_info=True)
        # Note: We do NOT re-raise this exception - activity logging failure should not block the deletion
        # The farmer has already been deleted from the database at this point


@receiver(post_delete, sender=FarmerHarvest)
def log_harvest_deletion(sender, instance, **kwargs):
    """
    Log when a FarmerHarvest is deleted.
    Signal failures are caught and logged but do not affect the main operation.

    IMPORTANT: This runs AFTER deletion is complete and committed to the database.
    By wrapping in try-except, we ensure deletion succeeds even if logging fails.
    """
    try:
        object_repr = f"Harvest: {instance.weight_on_delivery}kg from {instance.name or 'Farmer'}"
        content_type = ContentType.objects.get_for_model(FarmerHarvest)
        Activity.objects.create(
            user=None,  # Activity allows null user for system-triggered operations
            action=Activity.ACTION_DELETED,
            content_type=content_type,
            object_id=instance.harvest_id,
            object_repr=object_repr,
        )
        logger.info(f"[aggregation.signals] Logged harvest deletion: {instance.harvest_id}")
    except Exception as e:
        logger.error(f"[aggregation.signals] Failed to log harvest deletion for {instance.harvest_id}: {str(e)}", exc_info=True)
        # Note: We do NOT re-raise this exception - activity logging failure should not block the deletion
        # The harvest has already been deleted from the database at this point
