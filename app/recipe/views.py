"""
Views for Recipe.
"""
from recipe import serializers
from rest_framework import viewsets
from core.models import Recipe, Tag, Ingredient

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieves recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for the request."""
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    """View for manage Tags API."""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieves tags for authenticated API requests."""
        return self.queryset.all().order_by('name')

    def perform_create(self, serializer):
        """Create a new tag."""
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """Update a tag if the user is the creator."""
        tag = self.get_object()
        if tag.user != request.user:
            raise PermissionDenied('You do not have permission to update.')
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete a tag if the user is the creator."""
        tag = self.get_object()
        if tag.user != request.user:
            raise PermissionDenied('You do not have permission to delete.')
        return super().destroy(request, *args, **kwargs)


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieves ingredients for authenticated API requests."""
        return self.queryset.all().order_by('name')

    def perform_create(self, serializer):
        """Create a new ingredient."""
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """Update an ingredient if the user is the creator."""
        ingredient = self.get_object()
        if ingredient.user != request.user:
            raise PermissionDenied('You do not have permission to update.')
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete an ingredient if the user is the creator."""
        ingredient = self.get_object()
        if ingredient.user != request.user:
            raise PermissionDenied('You do not have permission to delete.')
        return super().destroy(request, *args, **kwargs)
