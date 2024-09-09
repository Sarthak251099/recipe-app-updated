"""
Views for Home API.
"""

from rest_framework import viewsets, status, generics

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from home import serializers
from core.models import Home, Inventory
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied
from home.permissions import IsHomeOwner, AddUserToHomePermissions
from django.contrib.auth import get_user_model


class HomeViewSet(viewsets.ModelViewSet):
    """Views to manage home API request."""
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
        user = request.user
        if not user.home:
            return Response(
                {'detail': 'No home found for the user.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        instance = self.get_object()
        if instance.id != user.home.id:
            return Response(
                {'detail': 'You do not have permission to update home.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete a home if the user is the home owner."""
        user = request.user
        if not user.home:
            return Response(
                {'detail': 'No home found for the user.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        home = self.get_object()
        if home.id != user.home.id:
            raise PermissionDenied('You do not have permission to delete.')
        return super().destroy(request, *args, **kwargs)


class InventoryFetchView(generics.ListAPIView):
    """View to fetch inventory list API requests."""
    serializer_class = serializers.InventorySerializer
    queryset = Inventory.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsHomeOwner]

    def get_queryset(self):
        """Return the list of inventory for authenticated user."""
        return (self.queryset
                .filter(home=self.request.user.home)
                .order_by('-id'))


class InventoryCreateView(generics.CreateAPIView):
    """View to create inventory item API request."""
    serializer_class = serializers.InventorySerializer
    queryset = Inventory.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsHomeOwner]

    def perform_create(self, serializer):
        """Create inventory for authenticated user's home"""
        serializer.save(home=self.request.user.home)


class InventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to update and retrieve Inventory items for home."""
    serializer_class = serializers.InventorySerializer
    queryset = Inventory.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsHomeOwner]


class AddUserToHomeView(generics.CreateAPIView):
    """View to add a user to logged in user's home."""
    serializer_class = serializers.AddUserHomeSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, AddUserToHomePermissions]

    def perform_create(self, serializer):
        user_id_in_payload = serializer.validated_data['user']
        user_to_add = get_user_model().objects.get(id=user_id_in_payload)
        auth_user = self.request.user
        user_to_add.home = auth_user.home
        user_to_add.save()
