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

    class Meta:
        model = Inventory
        fields = ['id', 'home', 'ingredient', 'amount']
        read_only_fields = ['id']
