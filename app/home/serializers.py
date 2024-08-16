"""
Serializers for home object.
"""

from rest_framework import serializers
from core.models import Home
from rest_framework.exceptions import ValidationError


class HomeSerializer(serializers.ModelSerializer):
    """Serializer for Home."""

    class Meta:
        model = Home
        fields = ['id', 'name', 'parameters']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create a home object in the system."""
        return Home.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update existing home in system."""
        user = self.context['request'].user
        if instance.id == user.home.id:
            home = super().update(instance, validated_data)
        else:
            return ValidationError('You do not have permissions.')
        return home
