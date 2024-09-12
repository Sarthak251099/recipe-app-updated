"""
Permissions for Home and Inventory API requests.
"""
from rest_framework import permissions
from rest_framework.exceptions import ValidationError, PermissionDenied
from core.models import Ingredient, Inventory, Recipe, FavHomeRecipe
from django.contrib.auth import get_user_model


class InventoryPermissions(permissions.BasePermission):
    """Custom permission for Inventory to ensure user owns home."""

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

        # For POST and UPDATE requests, check for duplicate inventory entries
        if (request.method in ['POST', 'PUT', 'PATCH'] and
                ingredient_in_payload):
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


class AddUserToHomePermissions(permissions.BasePermission):
    """Custom permission to check if user in payload exists in system and does
    not have a home assigned to them already. Check if auth user has a home."""

    def has_permission(self, request, view):
        """Check if user exists and no home assigned initailly."""

        user_in_payload = request.data.get('user')
        try:
            user = get_user_model().objects.get(id=user_in_payload)
        except get_user_model().DoesNotExist:
            raise ValidationError('Given user does not exist in system.')

        if user.home is not None:
            raise ValidationError('The user already has a home.')

        if not request.user.home:
            raise ValidationError(
                'You do not have a home to assign this user to.'
            )

        return True


class FavHomeRecipePermissions(permissions.BasePermission):
    """Custom permission to check if recipe being added/updated exists.
    Check if update/delete is done for objects that belong to user's home."""

    def has_permission(self, request, view):
        user = request.user
        if not user.home:
            raise ValidationError('You do not have a home.')

        recipe_in_payload = request.data.get('recipe')

        # Check if recipe exists in DB. Also check if duplicate recipe.
        if recipe_in_payload:
            try:
                recipe_id = int(recipe_in_payload)
                recipe = Recipe.objects.get(id=recipe_id)
            except (ValueError, Recipe.DoesNotExist):
                raise ValidationError('Given recipe does not exist.')
            else:
                if FavHomeRecipe.objects.filter(
                        home=user.home, recipe=recipe).exists():
                    raise ValidationError('Recipe already in Favourites.')
        return True

    def has_object_permission(self, request, view, obj):
        """Ensure user is updating the inventory of their home."""
        if obj.home.id != request.user.home.id:
            raise PermissionDenied('You are not authorized for this action.')
        return True
