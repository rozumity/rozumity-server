from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db.utils import IntegrityError

from .models import User, ClientProfile, ExpertProfile, StaffProfile


@receiver(post_save, sender=User, dispatch_uid='user.create_user_profile')
async def create_user_profile(sender, instance, created, **kwargs):
    profile_model = ClientProfile
    if instance.is_staff:
        profile_model = StaffProfile
    elif instance.is_expert:
        profile_model = ExpertProfile
    try:
        await profile_model.objects.acreate(user=instance)
    except IntegrityError:
        pass


@receiver(post_delete, sender=ClientProfile, dispatch_uid='clientProfile.delete_user')
@receiver(post_delete, sender=ExpertProfile, dispatch_uid='expertProfile.delete_user')
@receiver(post_delete, sender=StaffProfile, dispatch_uid='staffProfile.delete_user')
async def delete_profile(sender, instance, **kwargs):
    user = await User.objects.aget(email=await instance.user_email)
    await user.adelete()
