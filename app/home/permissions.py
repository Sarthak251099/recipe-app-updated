"""
Permissions for Inventory API requests.
"""
from rest_framework import permissions
from rest_framework.exceptions import ValidationError, PermissionDenied
from core.models import Ingredient, Inventory


class IsHomeOwner(permissions.BasePermission):
    """Custom permission to ensure user owns home."""

    def has_permission(self, request, view):
        user = request.user

        # Check if user has a home.
        if not user.home:
            raise PermissionDenied('You do not have a home.')

        # Handle ingredient validation in the payload
        ingredient_in_payload = request.data.get('ingredient')
        if ingredient_in_payload:
            try:
                ingredient_id = int(ingredient_in_payload)
                ingredient = Ingredient.objects.get(id=ingredient_id)
            except (ValueError, Ingredient.DoesNotExist):
                raise ValidationError(
                    'Provided Ingredient does not exist in the system.')

        # For POST requests, check for duplicate inventory entries
        if request.method == 'POST' and ingredient_in_payload:
            if Inventory.objects.filter(
                        home=user.home, ingredient=ingredient).exists():
                raise ValidationError(
                    'This ingredient already exists in your Inventory.')

        return True

    def has_object_permission(self, request, view, obj):
        """Ensure user is updating the inventory of their home."""
        if obj.home.id != request.user.home.id:
            raise PermissionDenied('You are not authorized for this action.')

        return True
