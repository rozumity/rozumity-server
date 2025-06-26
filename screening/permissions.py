from rest_framework.permissions import BasePermission
from accounts.permissions import IsClient
from rozumity.utils import rel


class IsResponsePublic(BasePermission):
    async def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method == 'POST':
            return await IsClient.has_permission(self, request, view)
        elif request.method in ["GET", "PUT", "PATCH"] and "pk" in view.kwargs.keys():
            if request.user.is_client:
                return True
            obj = await view.aget_object()
            client = await rel(obj, "client")
            expert_emails = set([await e.user_email for e in await client.experts])
            if obj.is_public and request.method == "GET":
                return True
            if obj.is_public_expert and request._user.email in expert_emails:
                return True
            return False
        return True
