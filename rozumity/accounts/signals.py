# https://simpleisbetterthancomplex.com/tutorial/2016/07/28/how-to-create-django-signals.html
# https://stackoverflow.com/questions/62864963/best-approach-to-auto-create-profile-object-upon-user-creation-in-django
from django.db.models.signals import post_save
from rozumity.receivers import async_receiver as receiver

from .models import User, ClientProfile, ExpertProfile, StaffProfile


@receiver(post_save, sender=User, dispatch_uid='user.create_user_profile')
def create_user_profile(sender, instance, created, **kwargs):
    if instance.is_staff:
        StaffProfile.objects.create(user=instance)
    elif instance.is_expert:
        ExpertProfile.objects.create(user=instance)
    else:
        ClientProfile.objects.create(user=instance)


@receiver(post_save, sender=User, dispatch_uid='user.save_user_profile')
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
