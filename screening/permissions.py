from rest_framework.permissions import BasePermission
from rozumity.utils import rel


class IsResponsePublic(BasePermission):
    async def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method == "POST":
            return request.user.email == request.data.email
        elif request.method in ["GET", "PUT", "PATCH"]:
            email = request.user.email
            model = view.serializer_class.Meta.model
            obj = await model.objects.aget(**{
                model._meta.pk.name: view.kwargs.get('pk')
            })
            client = await rel(obj, "client")
            is_client_owner = await client.user_email == email
            if obj.is_public and request.method == "GET":
                return True
            elif obj.is_public_expert and await client.expert_email == email:
                return True
            else:
                return is_client_owner
        return False
