
from rest_framework.permissions import BasePermission, IsAdminUser, IsAuthenticated


class IsAdmin(IsAdminUser):
    async def has_permission(self, request, view):
        return request.user.is_staff


class IsUser(IsAuthenticated):
    async def has_permission(self, request, view):
        return request.user.is_authenticated


class IsAdminListUserCreate(BasePermission):
    async def has_permission(self, request, view):
        return all((
            request.user.is_authenticated,
            request.method == "POST" or (
                request.method == "GET" and request.user.is_staff
            )
        ))


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
