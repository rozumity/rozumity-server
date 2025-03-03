from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django.db.utils import IntegrityError

from .models import User, ClientProfile, ExpertProfile, StaffProfile


@receiver(post_save, sender=User, dispatch_uid='user.create_user_profile')
async def create_user_profile(sender, instance, created, **kwargs):
    profile_model = ExpertProfile if instance.is_expert else ClientProfile
    if instance.is_staff:
        profile_model = StaffProfile
    try:
        await profile_model.objects.acreate(user=instance)
    except IntegrityError:
        pass


#@receiver(post_save, sender=User, dispatch_uid='user.save_user_profile')
#async def save_user_profile(sender, instance, **kwargs):
#    await instance.profile.asave()
