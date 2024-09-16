"""
Permissions for utility method API requests.
"""

from rest_framework import permissions
from rest_framework.exceptions import ValidationError


class HasHome(permissions.BasePermission):
    """Custom permission to check if the user has a home."""

    def has_permission(self, request, view):
        user = request.user
        home = user.home

        if not home:
            raise ValidationError('You do not have a home assigned.')

        return True
