
from rest_framework.permissions import BasePermission, IsAdminUser, IsAuthenticated
from django.db.models import ForeignKey
from rozumity.utils import rel


class IsAdmin(IsAdminUser):
    async def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class IsUser(IsAuthenticated):
    async def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class AsyncOrPermission(BasePermission):
    """
    DRF Or adrf.
    permission_classes = (AsyncOrPermission(IsAdmin(), IsUser()),)
    """
    def __init__(self, *perms):
        self.perms = perms

    async def has_permission(self, request, view):
        for perm in self.perms:
            if await perm.has_permission(request, view):
                return True
        return False

    async def has_object_permission(self, request, view, obj):
        for perm in self.perms:
            if await perm.has_object_permission(request, view, obj):
                return True
        return False


class AsyncAndPermission(BasePermission):
    def __init__(self, *perms):
        self.perms = perms

    async def has_permission(self, request, view):
        for perm in self.perms:
            if not await perm.has_permission(request, view):
                return False
        return True

    async def has_object_permission(self, request, view, obj):
        for perm in self.perms:
            if not await perm.has_object_permission(request, view, obj):
                return False
        return True


class IsCreatorOwner(BasePermission):
    async def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        model = getattr(view.serializer_class.Meta, "model", None)
        if request.method == "POST":
            return user.email == request.data.get("email")
        elif request.method in ["GET", "PUT", "PATCH"]:
            pk = view.kwargs.get('pk')
            if not (model and pk):
                return False
            obj = await model.objects.aget(**{model._meta.pk.name: pk})
            # Проверяем по id, а не email (актуально для новых моделей)
            if hasattr(obj, "client_id") and obj.client_id == user.id:
                return True
            if hasattr(obj, "expert_id") and obj.expert_id == user.id:
                return True
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
                if hasattr(obj, "client.pk"):
                    return obj.client.pk == email
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
