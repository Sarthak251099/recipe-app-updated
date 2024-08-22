"""
Views for Inventory.
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from inventory import serializers
from core.models import Inventory
from rest_framework.exceptions import ValidationError


class InventoryViewSet(viewsets.ModelViewSet):
    """View for inventory serializer."""
    serializer_class = serializers.InventorySerializer
    queryset = Inventory.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.home:
            return self.queryset.filter(home=user.home).order_by('-id')
        else:
            raise ValidationError('User has no home.')

    def perform_create(self, serializer):
        user = self.request.user
        home = serializer.validated_data['home']
        if user.home and user.home == home:
            serializer.save()
        else:
            raise ValidationError('Request not authorized for the user.')

    def perform_update(self, serializer):
        user = self.request.user
        if not user.home:
            raise ValidationError('User does not have a home.')
        if "home" in serializer.validated_data:
            home = serializer.validated_data['home']
            if user.home == home:
                serializer.save()
            else:
                raise ValidationError('Request not authorized for the user.')
        else:
            serializer.save()
