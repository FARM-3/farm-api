"""
Signals for production app to automatically log activities
when Harvests or Block objects are created, updated, or deleted.

Note: All signal handlers include try-except blocks to prevent signal errors
from breaking the main operation (create/update/delete). Activity logging
failures are logged but do not affect data integrity.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Harvests, Block
from activities.models import Activity
from activities.middleware import get_current_user

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Harvests)
def log_harvest_activity(sender, instance, created, **kwargs):
    """
    Log when a Harvest is created or updated.
    Signal failures are caught and logged but do not affect the main operation.
    """
    try:
        if created:
            action = Activity.ACTION_CREATED
            object_repr = f"Harvest: {instance.weight_on_delivery}kg from {instance.worker_name}"
        else:
            action = Activity.ACTION_UPDATED
            object_repr = f"Harvest: {instance.weight_on_delivery}kg from {instance.worker_name}"

        content_type = ContentType.objects.get_for_model(Harvests)
        user = get_current_user()
        Activity.objects.create(
            user=user,
            action=action,
            content_type=content_type,
            object_id=instance.harvest_id,
            object_repr=object_repr,
        )
        logger.info(f"[production.signals] Logged production harvest {action}: {instance.harvest_id} by {user or 'System'}")
    except Exception as e:
        logger.error(f"[production.signals] Failed to log production harvest activity for {instance.harvest_id}: {str(e)}", exc_info=True)
        # Note: We do NOT re-raise this exception - activity logging failure should not break the operation


@receiver(post_save, sender=Block)
def log_block_activity(sender, instance, created, **kwargs):
    """
    Log when a Block is created or updated.
    Signal failures are caught and logged but do not affect the main operation.
    """
    try:
        if created:
            action = Activity.ACTION_CREATED
            object_repr = f"Block: {instance.block_id}"
        else:
            action = Activity.ACTION_UPDATED
            object_repr = f"Block: {instance.block_id}"

        content_type = ContentType.objects.get_for_model(Block)
        user = get_current_user()
        Activity.objects.create(
            user=user,
            action=action,
            content_type=content_type,
            object_id=instance.block_id,
            object_repr=object_repr,
        )
        logger.info(f"[production.signals] Logged block {action}: {instance.block_id} by {user or 'System'}")
    except Exception as e:
        logger.error(f"[production.signals] Failed to log block activity for {instance.block_id}: {str(e)}", exc_info=True)
        # Note: We do NOT re-raise this exception - activity logging failure should not break the operation


@receiver(post_delete, sender=Harvests)
def log_harvest_deletion(sender, instance, **kwargs):
    """
    Log when a Harvest is deleted.
    Signal failures are caught and logged but do not affect the main operation.

    IMPORTANT: This runs AFTER deletion is complete and committed to the database.
    By wrapping in try-except, we ensure deletion succeeds even if logging fails.
    """
    try:
        object_repr = f"Harvest: {instance.weight_on_delivery}kg from {instance.worker_name}"
        content_type = ContentType.objects.get_for_model(Harvests)
        user = get_current_user()
        Activity.objects.create(
            user=user,
            action=Activity.ACTION_DELETED,
            content_type=content_type,
            object_id=instance.harvest_id,
            object_repr=object_repr,
        )
        logger.info(f"[production.signals] Logged production harvest deletion: {instance.harvest_id} by {user or 'System'}")
    except Exception as e:
        logger.error(f"[production.signals] Failed to log production harvest deletion for {instance.harvest_id}: {str(e)}", exc_info=True)
        # Note: We do NOT re-raise this exception - activity logging failure should not block the deletion
        # The harvest has already been deleted from the database at this point


@receiver(post_delete, sender=Block)
def log_block_deletion(sender, instance, **kwargs):
    """
    Log when a Block is deleted.
    Signal failures are caught and logged but do not affect the main operation.

    IMPORTANT: This runs AFTER deletion is complete and committed to the database.
    By wrapping in try-except, we ensure deletion succeeds even if logging fails.
    """
    try:
        object_repr = f"Block: {instance.block_id}"
        content_type = ContentType.objects.get_for_model(Block)
        user = get_current_user()
        Activity.objects.create(
            user=user,
            action=Activity.ACTION_DELETED,
            content_type=content_type,
            object_id=instance.block_id,
            object_repr=object_repr,
        )
        logger.info(f"[production.signals] Logged block deletion: {instance.block_id} by {user or 'System'}")
    except Exception as e:
        logger.error(f"[production.signals] Failed to log block deletion for {instance.block_id}: {str(e)}", exc_info=True)
        # Note: We do NOT re-raise this exception - activity logging failure should not block the deletion
        # The block has already been deleted from the database at this point
