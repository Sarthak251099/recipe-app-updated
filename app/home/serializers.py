"""
Serializers for home object.
"""

from rest_framework import serializers
from core.models import Home, Inventory


class HomeSerializer(serializers.ModelSerializer):
    """Serializer for Home."""

    class Meta:
        model = Home
        fields = ['id', 'name', 'parameters']
        read_only_fields = ['id']


class InventorySerializer(serializers.ModelSerializer):
    """Serializer object for Inventory."""

    ingredient_name = serializers.ReadOnlyField(source='ingredient.name')

    class Meta:
        model = Inventory
        fields = ['id', 'ingredient', 'ingredient_name', 'amount']
        read_only_fields = ['id', 'ingredient_name']


class AddUserHomeSerializer(serializers.Serializer):
    """Serializer object for adding user to home."""
    user = serializers.IntegerField()


class RemoveUserFromHomeSerializer(serializers.Serializer):
    """Serializer for removing user from home."""
    pass
