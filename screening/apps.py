from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ScreeningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'screening'
    verbose_name = _('Screening')
