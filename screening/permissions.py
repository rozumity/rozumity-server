from rest_framework.permissions import BasePermission
from rozumity.utils import rel


class IsResponsePublic(BasePermission):
    async def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method == "POST":
            return request.user.email == request.data.email
        elif request.method in ["GET", "PUT", "PATCH"] and "pk" in view.kwargs.keys():
            email = request.user.email
            model = view.get_serializer_class().Meta.model
            obj = await model.objects.aget(**{
                model._meta.pk.name: view.kwargs.get('pk')
            })
            client = await rel(obj, "client")
            if await client.user_email == email:
                return True
            if obj.is_public and request.method == "GET":
                return True
            if obj.is_public_expert and await client.expert_email == email:
                return True
            return False
        return True
