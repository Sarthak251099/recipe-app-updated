"""
Serializers for home object.
"""

from rest_framework import serializers
from core.models import Home, Inventory
from rest_framework.exceptions import ValidationError


class HomeSerializer(serializers.ModelSerializer):
    """Serializer for Home."""

    class Meta:
        model = Home
        fields = ['id', 'name', 'parameters']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        """Update existing home in system."""
        user = self.context['request'].user
        if instance.id == user.home.id:
            home = super().update(instance, validated_data)
        else:
            return ValidationError('You do not have permissions.')
        return home


class InventorySerializer(serializers.ModelSerializer):
    """Serializer object for Inventory."""

    class Meta:
        model = Inventory
        fields = ['id', 'home', 'ingredient', 'amount']
        read_only_fields = ['id']
