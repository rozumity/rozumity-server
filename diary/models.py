from django.db import models
from accounts.models import ClientProfile
from django.utils.translation import gettext_lazy as _

# Create your models here.


#class Diary(models.Model):
#    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, to_field="user")
#    theme = models.SmallIntegerField(choices=((0, _('light')), (1, _('dark'))), default=0)
#    has_health_attention = models.BooleanField(default=False)
#    date_start = models.DateTimeField(default=timezone.now)
#    
#    class Meta:
#        verbose_name = _("Diary")
#        verbose_name_plural = _("Diaries")
#    
#    def __str__(self):
#        return f'{self.client} - {self.expert}'
