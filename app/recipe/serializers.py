"""
Serializer for Recipe object.
"""

from core.models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
)
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

    created_by = serializers.ReadOnlyField(source='user.name')

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'link', 'created_by']
        read_only_fields = ['id', 'created_by']


class RecipeDetailSerializer(RecipeSerializer):
    """Serializers for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Serializers for recipe ingredients."""

    recipe_name = serializers.ReadOnlyField(source='recipe.title')
    ingredient_name = serializers.ReadOnlyField(source='ingredient.name')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'recipe', 'recipe_name', 'ingredient',
                  'ingredient_name', 'amount', 'mandatory', 'amount_unit']
        read_only_fields = ['id', 'recipe_name', 'ingredient_name']
