from rest_framework_simplejwt.authentication import JWTAuthentication
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

class AsyncJWTAuthentication(JWTAuthentication):
    async def authenticate(self, request):
        auth_result = await sync_to_async(super().authenticate)(request)
        if auth_result is None:
            return None
        user, token = auth_result
        User = get_user_model()
        user_with_profiles = await User.objects.prefetch_related(
            'clientprofile', 'expertprofile', 'staffprofile',
        ).aget(pk=user.pk)
        user.client_profile = getattr(user_with_profiles, 'clientprofile', None)
        user.expert_profile = getattr(user_with_profiles, 'expertprofile', None)
        user.staff_profile = getattr(user_with_profiles, 'staffprofile', None)
        return (user, token)
