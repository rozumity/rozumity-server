
from rest_framework.permissions import BasePermission, IsAdminUser, IsAuthenticated


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
        else:
            return request.user.email == view.kwargs.get('pk')


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
