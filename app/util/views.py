"""
Views for Utility functions API Requests.
"""
from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from util.serializers import SuggestRecipeSerializer
from util.permissions import HasHome
from core.models import (
    FavHomeRecipe,
    RecipeIngredient,
    Inventory,
)


class SuggestRecipeView(generics.ListAPIView):
    """Suggest recipe based on favorite recipe for a home considering
    ingredients available in inventory and ingredients required for recipe.
    Also considering factor is how recently is the recipe cooked."""

    serializer_class = SuggestRecipeSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, HasHome]

    def get_queryset(self):
        """Get a suggested recipe."""
        home = self.request.user.home
        fav_recipes = self.get_fav_recipes_for_home(home)
        for fav_recipe in fav_recipes:
            if self.are_ingredients_available(home, fav_recipe.recipe):
                return [fav_recipe]
        return []

    def get_fav_recipes_for_home(self, home):
        """Fetch all favorite recipes of a home, ordered by
        least recently cooked recipe."""
        return FavHomeRecipe.objects.filter(home=home).order_by('last_cooked')

    def are_ingredients_available(self, home, recipe):
        """Check if all ingredients required for a recipe
        are available in the home inventory."""
        required_ingredients = RecipeIngredient.objects.filter(
            recipe=recipe,
            mandatory=True
        )
        for ing in required_ingredients:
            inventory = Inventory.objects.filter(
                home=home,
                ingredient=ing.ingredient
            ).first()
            if not inventory or inventory.amount < ing.amount:
                return False
        return True

    def list(self, request, *args, **kwargs):
        """Override to customize the response."""
        queryset = self.get_queryset()
        if not queryset:
            return Response(
                {'detail': 'No suitable recipe with available ingredients.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
