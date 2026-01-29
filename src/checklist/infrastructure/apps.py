from django.apps import AppConfig


class ChecklistConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    models_module = "checklist.domain.models"
    name = "checklist"
    label = "checklist"
