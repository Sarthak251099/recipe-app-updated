"""
Views for Home API.
"""

from rest_framework import viewsets, status, generics

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from home import serializers
from core.models import Home, Inventory, FavHomeRecipe
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied
from home.permissions import (
    InventoryPermissions,
    AddUserToHomePermissions,
    # FavHomeRecipePermissions,
)
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
    permission_classes = [IsAuthenticated, InventoryPermissions]

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
    permission_classes = [IsAuthenticated, InventoryPermissions]

    def perform_create(self, serializer):
        """Create inventory for authenticated user's home"""
        serializer.save(home=self.request.user.home)


class InventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to update and retrieve Inventory items for home."""
    serializer_class = serializers.InventorySerializer
    queryset = Inventory.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, InventoryPermissions]


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


class RemoveUserFromHomeView(generics.GenericAPIView):
    """View to remove user from home and delete home if last user."""
    serializer_class = serializers.RemoveUserFromHomeSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        home = user.home
        if not home:
            return Response(
                {'detail': 'User is not associated with any home.'},
                status=status.HTTP_400_BAD_REQUEST)
        user.home = None
        user.save()

        # Check if the home is now empty (i.e., no users belong to it)
        if not get_user_model().objects.filter(home=home).exists():
            home.delete()
        return Response(
            {'detail': 'User removed from home.'},
            status=status.HTTP_200_OK)


class FavHomeRecipeListView(generics.ListAPIView):
    """View to manage Favourite home recipe API requests."""
    serializer_class = serializers.FavHomeRecipeSerializer
    queryset = FavHomeRecipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return the list of fav recipes for authenticated user's home."""
        return (self.queryset
                .filter(home=self.request.user.home)
                .order_by('-id'))


class FavHomeRecipeCreateView(generics.CreateAPIView):
    """View to add a fav recipe to user's home."""
    serializer_class = serializers.FavHomeRecipeSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(home=self.request.user.home, rating=8)
