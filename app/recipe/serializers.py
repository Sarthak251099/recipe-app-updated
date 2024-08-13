"""
Serializer for Recipe object.
"""

from core.models import Recipe
from rest_framework import serializers


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe."""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'link']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create and return recipe object."""
        recipe = Recipe.objects.create(**validated_data)
        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    """Serializers for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
