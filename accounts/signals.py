from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from .models import User, ClientProfile, ExpertProfile, StaffProfile


@receiver(post_save, sender=User, dispatch_uid='user.create_user_profile')
async def create_user_profile(sender, instance, created, **kwargs):
    profile_model = ClientProfile
    if instance.is_staff:
        profile_model = StaffProfile
    elif instance.is_expert:
        profile_model = ExpertProfile
    await profile_model.objects.aget_or_create(user=instance)


@receiver(post_delete, sender=ClientProfile, dispatch_uid='clientProfile.delete_user')
@receiver(post_delete, sender=ExpertProfile, dispatch_uid='expertProfile.delete_user')
@receiver(post_delete, sender=StaffProfile, dispatch_uid='staffProfile.delete_user')
def delete_profile(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()
