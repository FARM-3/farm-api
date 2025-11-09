from django.apps import AppConfig


class AggregationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aggregation'

    def ready(self):
        import aggregation.signals  # noqa: F401
