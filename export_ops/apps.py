from django.apps import AppConfig


class ExportOpsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'export_ops'

    def ready(self):
        import export_ops.signals  # noqa: F401
