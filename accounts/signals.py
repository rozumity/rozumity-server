from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import User, ClientProfile, ExpertProfile, StaffProfile


@receiver(post_save, sender=User, dispatch_uid='user.create_user_profile')
async def create_user_profile(sender, instance, created, **kwargs):
    profile_model = ClientProfile
    if instance.is_expert:
        profile_model = ExpertProfile
    elif instance.is_staff:
        profile_model = StaffProfile
    await profile_model.objects.aget_or_create(user=instance)
