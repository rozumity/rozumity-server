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
            if obj.is_public and request.method == "GET":
                return True
            if obj.is_public_expert and await client.expert_email == request.user.email:
                return True
            return False
        return True
