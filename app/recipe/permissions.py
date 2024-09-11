"""
Permissions for recipe API requests.
"""
from rest_framework import permissions
from rest_framework.exceptions import ValidationError, PermissionDenied
from core.models import Tag, Ingredient


class TagPermissions(permissions.BasePermission):
    """Custom permission to check tag API requests."""

    def has_permission(self, request, view):
        """Check if a tag already exists for create requests."""

        if request.method == 'POST':
            tag_name_in_payload = request.data.get('name')
            exist = Tag.objects.filter(name=tag_name_in_payload).exists()
            if exist:
                raise ValidationError('Tag with the name already exists.')

        return True

    def has_object_permission(self, request, view, obj):
        """Do not allow users to update/delete tags created by others."""
        if obj.user != request.user:
            raise PermissionDenied(
                'You are not authorized to perform this action.'
            )
        return True


class IngredientPermissions(permissions.BasePermission):
    """Custom permission to check ingredient API requests."""

    def has_permission(self, request, view):
        """Check if an ingredient already exists for create requests."""

        if request.method == 'POST':
            ing_name_payload = request.data.get('name')
            exist = Ingredient.objects.filter(name=ing_name_payload).exists()
            if exist:
                raise ValidationError(
                    'Ingredient with the name already exists.')
        return True

    def has_object_permission(self, request, view, obj):
        """Do not allow users to update/delete ingredient created by others."""
        if obj.user != request.user:
            raise PermissionDenied(
                'You are not authorized to perform this action.'
            )
        return True


class RecipePermission(permissions.BasePermission):
    """Custom permission to check recipe API requests."""

    def has_object_permission(self, request, view, obj):
        """Do not allow users to update/delete recipe created by others."""
        if obj.user != request.user:
            raise PermissionDenied(
                'You are not authorized to perform this action.'
            )
        return True
