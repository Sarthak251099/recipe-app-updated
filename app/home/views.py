"""
Views for Home API.
"""

from rest_framework import viewsets, status

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from home import serializers
from core.models import Home, Inventory
from rest_framework.exceptions import ValidationError


class HomeViewSet(viewsets.ModelViewSet):
    """Views for manage home API request."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.HomeSerializer
    queryset = Home.objects.all()

    def get_queryset(self):
        """Return home object for authenticated user."""
        user = self.request.user
        if user.home:
            return self.queryset.filter(id=user.home.id).order_by('-id')
        else:
            return Home.objects.none()

    def perform_create(self, serializer):
        """Create and return home object."""
        user = self.request.user
        if user.home:
            raise ValidationError('You already have a home.')
        home = serializer.save()
        user.home = home
        user.save()
        return home

    def update(self, request, *args, **kwargs):
        """Update and return home object."""
        user = self.request.user
        if not user.home:
            return Response(
                {'detail': 'No home found for the user.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return super().update(request, *args, **kwargs)


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
