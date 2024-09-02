"""
Views for Home API.
"""

from rest_framework import viewsets, status, generics

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from home import serializers
from core.models import Home, Inventory, Ingredient
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied


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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.home:
            return (
                self.queryset
                .filter(home=user.home)
                .order_by('-id')
                .select_related('ingredient')
                )
        else:
            raise ValidationError('User does not have a home.')


class InventoryCreateView(generics.CreateAPIView):
    """View to create inventory item API request."""
    serializer_class = serializers.InventorySerializer
    queryset = Inventory.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Create and return a Inventory object."""
        user = self.request.user

        if not user.home:
            raise ValidationError('User does not have a home.')

        request_home = serializer.validated_data.get('home')
        if request_home.id != user.home.id:
            raise PermissionDenied(
                'You are not authorized to add to this inventory.')

        ingredient = serializer.validated_data.get('ingredient')
        exist = Ingredient.objects.filter(id=ingredient.id).exists()

        if not exist:
            raise ValidationError('Given ingredient does not exists.')

        serializer.save()


class InventoryUpdateView(generics.RetrieveUpdateAPIView):
    """View to update and retrieve Inventory items for home."""
    serializer_class = serializers.InventorySerializer
    queryset = Inventory.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return detailed Inventory item for home."""
        user = self.request.user

        if not user.home:
            raise ValidationError('User does not have a home.')

        return (
            self.queryset
            .filter(home=user.home)
            .select_related('ingredient')
            )

    def perform_update(self, serializer):
        """Update inventory item for user's home."""
        user = self.request.user

        if not user.home:
            raise ValidationError('User does not have a home.')

        if serializer.instance.home != user.home:
            raise PermissionDenied(
                'You do not have permissions to update for this home.')

        home_in_payload = serializer.validated_data.get('home')

        if home_in_payload and home_in_payload != user.home:
            raise PermissionDenied(
                'You do not have permissions to update for this home.')

        serializer.save()
