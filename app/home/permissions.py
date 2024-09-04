"""
Permissions for Inventory API requests.
"""
from rest_framework import permissions
from rest_framework.exceptions import ValidationError, PermissionDenied
from core.models import Ingredient


class IsHomeOwner(permissions.BasePermission):
    """Custom permission to check if the user is the owner of the home."""

    def has_permission(self, request, view):
        user = request.user
        if not user.home:
            raise ValidationError('User does not have a home.')

        home_in_payload = request.data.get('home')

        if home_in_payload and int(home_in_payload) != user.home.id:
            raise PermissionDenied(
                'You do not have permissions to perform this action.')
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        ingredient_in_payload = request.data.get('ingredient')

        if ingredient_in_payload:
            ing = Ingredient.objects.filter(id=int(ingredient_in_payload))
            if not ing.exists():
                raise ValidationError(
                    'Provided Ingredient does not exist in the system')

        if request.method in ['PATCH', 'PUT', 'DELETE']:
            if obj.home != user.home:
                raise PermissionDenied(
                    'You do not have permissions to \
modify this inventory item.')

        return True
