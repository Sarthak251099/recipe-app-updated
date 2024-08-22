"""
Serializer for Inventory.
"""

from rest_framework import serializers
from core.models import Inventory


class InventorySerializer(serializers.ModelSerializer):
    """Serializer object for Inventory."""

    class Meta:
        model = Inventory
        fields = ['id', 'home', 'ingredient', 'amount']
        read_only_fields = ['id']
