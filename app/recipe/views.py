"""
Views for Recipe.
"""
from recipe import serializers
from rest_framework import viewsets
from core.models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from recipe.permissions import (
    TagPermissions,
    IngredientPermissions,
    RecipePermission,
    RecipeIngredientPermission,
)


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, RecipePermission]

    def get_queryset(self):
        """Retrieves recipes for authenticated user."""
        return self.queryset.all().order_by('-id')

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
    permission_classes = [IsAuthenticated, TagPermissions]

    def get_queryset(self):
        """Retrieves tags for authenticated API requests."""
        return self.queryset.all().order_by('name')

    def perform_create(self, serializer):
        """Create a new tag."""
        serializer.save(user=self.request.user)


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IngredientPermissions]

    def get_queryset(self):
        """Retrieves ingredients for authenticated API requests."""
        return self.queryset.all().order_by('name')

    def perform_create(self, serializer):
        """Create a new ingredient."""
        serializer.save(user=self.request.user)


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    """Views to manage recipe ingredient API requests."""
    serializer_class = serializers.RecipeIngredientSerializer
    queryset = RecipeIngredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, RecipeIngredientPermission]

    def get_queryset(self):
        """Retrieve ingredients required for recipe."""
        return self.queryset.all().order_by('-id')
