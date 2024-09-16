"""
Serializers for Utility method API requests.
"""

from rest_framework import serializers
from core.models import FavHomeRecipe


class SuggestRecipeSerializer(serializers.ModelSerializer):
    """Serializer for suggesting favorite recipe based on
    ingredients available in home and required ingredients for recipe."""

    recipe_title = serializers.ReadOnlyField(source='recipe.title')

    class Meta:
        model = FavHomeRecipe
        fields = ['id', 'recipe',
                  'recipe_title', 'last_cooked', 'rating']
