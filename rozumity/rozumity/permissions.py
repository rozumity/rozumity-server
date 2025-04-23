
from rest_framework import permissions


class AuthReadStaffWritePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return all((
            request.user.is_authenticated,
            request.method == 'GET' or request.user.is_staff
        ))
