from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from adrf_caching.utils import CacheUtils

from rozumity.utils import rel

from .models import (
    User, ClientProfile, ExpertProfile,
    StaffProfile, Education, TherapyContract
)


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

# --- Education Signals ---

@receiver(post_save, sender=Education)
async def invalidate_expert_on_edu_save(sender, instance, **kwargs):
    """Update expert's version when education is added/updated."""
    expert = await rel(instance, "expert")
    if expert:
        await CacheUtils.incr_user_version(expert.user_id)


@receiver(post_delete, sender=Education)
async def invalidate_expert_on_edu_delete(sender, instance, **kwargs):
    """Update expert's version when education is deleted."""
    # При видаленні об'єкт ще має дані в пам'яті, тому rel спрацює
    expert = await rel(instance, "expert")
    if expert:
        await CacheUtils.incr_user_version(expert.user_id)

# --- Contract Signals ---

@receiver(post_save, sender=TherapyContract)
async def invalidate_contract_parties_on_save(sender, instance, **kwargs):
    """Update both client and expert versions when contract changes."""
    client = await rel(instance, "client")
    expert = await rel(instance, "expert")
    if client:
        await CacheUtils.incr_user_version(client.user_id)
    if expert:
        await CacheUtils.incr_user_version(expert.user_id)


@receiver(post_delete, sender=TherapyContract)
async def invalidate_contract_parties_on_delete(sender, instance, **kwargs):
    """Update both parties when contract is removed."""
    client = await rel(instance, "client")
    expert = await rel(instance, "expert")
    if client:
        await CacheUtils.incr_user_version(client.user_id)
    if expert:
        await CacheUtils.incr_user_version(expert.user_id)
