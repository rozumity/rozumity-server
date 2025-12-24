from rest_framework import permissions
from accounts.utils import get_profile


class IsEducationOwner(permissions.BasePermission):
    async def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_expert:
            profile = await get_profile(request)
            pk = view.kwargs.get('pk')
            async for education in profile.education.all():
                if education.id == pk:
                    return True
        return False
