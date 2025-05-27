
from rest_framework.permissions import BasePermission, IsAdminUser, IsAuthenticated
from django.db.models import ForeignKey
from rozumity.utils import rel


class IsAdmin(IsAdminUser):
    async def has_permission(self, request, view):
        return request.user.is_staff


class IsUser(IsAuthenticated):
    async def has_permission(self, request, view):
        return request.user.is_authenticated


class IsCreatorOwner(BasePermission):
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
            if hasattr(obj, "client_id"):
                return obj.client_id == email
            elif hasattr(obj, "expert_id"):
                return obj.expert_id == email
            else:
                return False
        return False


class IsCreatorOwnerRecursive(BasePermission):
    async def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method == "POST":
            return request.user.email == request.data.email
        if request.method == "GET":
            email = request.user.email
            model = view.serializer_class.Meta.model
            obj = await model.objects.aget(**{
                model._meta.pk.name: view.kwargs.get('pk')
            })
            async def is_owner(obj, email):
                if hasattr(obj, "client_id"):
                    return obj.client_id == email
                elif hasattr(obj, "expert_id"):
                    return obj.expert_id == email
                related_objs = [
                    await rel(obj, field.name) for field 
                    in obj.__class__._meta.fields
                    if isinstance(field, ForeignKey)
                ]
                if len(related_objs):
                    for obj in related_objs:
                        if await is_owner(obj, email):
                            return True
                return False
            return await is_owner(obj, email)
        return False


class IsAdminCreateUserList(BasePermission):
    async def has_permission(self, request, view):
        return all((
            request.user.is_authenticated,
            request.method == "GET" or (
                request.method == "POST" and request.user.is_staff
            )
        ))


class IsAdminUpdateDeleteUserRead(BasePermission):
    async def has_permission(self, request, view):
        return all((
            request.user.is_authenticated,
            request.method == "GET" or (
                request.method in ["PUT", "PATCH", "DELETE"]
                and request.user.is_staff
            )
        ))


class IsAdminReadUserUpdate(BasePermission):
    async def has_permission(self, request, view):
        return all((
            request.user.is_authenticated,
            request.method in ["PUT", "PATCH"] or (
                request.method == "GET"
                and request.user.is_staff
            )
        ))
