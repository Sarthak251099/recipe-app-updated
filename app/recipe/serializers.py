"""
Serializer for Recipe object.
"""

from core.models import Recipe, Tag, Ingredient
from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredients."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe."""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'link']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Serializers for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
