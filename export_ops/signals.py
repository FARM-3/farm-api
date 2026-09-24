from django.db.models.signals import post_save
from django.dispatch import receiver

from processing.models import Bagging

from .services import sync_inventory_from_bagging


@receiver(post_save, sender=Bagging)
def bagging_sync_inventory(sender, instance, **kwargs):
    sync_inventory_from_bagging(instance)
