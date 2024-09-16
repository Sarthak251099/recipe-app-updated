"""
Test recipe ingredient API requests.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from recipe.helper_method import (
    create_user,
    create_recipe,
    create_ingredient,
    create_recipe_ingredient,
)
from recipe.serializers import RecipeIngredientSerializer
from core.models import RecipeIngredient

RECIPE_INGREDIENT_URL = reverse('recipe:recipeingredient-list')


def detail_url(recipe_ingredient_id):
    return reverse(
        'recipe:recipeingredient-detail',
        args=[recipe_ingredient_id],
    )


class PublicRecipeIngredientRequests(TestCase):
    """Public recipe ingredient requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RECIPE_INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeIngredientRequests(TestCase):
    """Tests for authenticated user's requests."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='Testpass123')
        self.client = APIClient()
        self.recipe = create_recipe(user=self.user)
        self.ingredient = create_ingredient(user=self.user)
        self.client.force_authenticate(self.user)

    def test_fetch_all_recipe_ingredients(self):
        """Fetch all recipe ingredients."""
        create_recipe_ingredient(
            recipe=self.recipe,
            ingredient=self.ingredient
        )
        res = self.client.get(RECIPE_INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe_ingredient = RecipeIngredient.objects.all().order_by('-id')
        serializer = RecipeIngredientSerializer(recipe_ingredient, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe_ingredient(self):
        """Test create new recipe ingredient."""
        payload = {
            'recipe': self.recipe.id,
            'ingredient': self.ingredient.id,
            'amount': 280,
            'amount_unit': 'tablespoon',
            'mandatory': False,
        }
        res = self.client.post(RECIPE_INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipeingredient = RecipeIngredient.objects.filter(
            recipe=self.recipe,
            ingredient=self.ingredient,
        )
        self.assertTrue(recipeingredient.exists())

    def test_create_recipe_ingredient_for_recipe_not_created_by_user(self):
        """Test adding recipe ingredient for a recipe which
        is not created by the user is unsuccessful."""
        new_user = create_user(
            email='sarthak@example.com',
            password='banana12'
        )
        recipe = create_recipe(user=new_user, title='Custard')
        payload = {
            'recipe': recipe.id,
            'ingredient': self.ingredient.id,
            'amount': 280,
            'amount_unit': 'tablespoon',
            'mandatory': False,
        }
        res = self.client.post(RECIPE_INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_recipe_ingredient(self):
        """Test updating recipe ingredient is success."""
        recipe_ingredient = create_recipe_ingredient(
            recipe=self.recipe,
            ingredient=self.ingredient)
        url = detail_url(recipe_ingredient.id)

        recipe = create_recipe(user=self.user, title='Custard')
        payload = {
            'recipe': recipe.id,
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe_ingredient.refresh_from_db()
        self.assertEqual(recipe_ingredient.recipe, recipe)

    def test_update_recipe_ingredient_not_created_by_user(self):
        """Test updating an instance of recipe ingredient when
        the user did not originally create the instance."""
        new_user = create_user(
            email='sarthak@example.com',
            password='banana12'
        )
        recipe = create_recipe(user=new_user, title='Custard')
        recipe_ingredient = create_recipe_ingredient(
            recipe=recipe,
            ingredient=self.ingredient)
        url = detail_url(recipe_ingredient.id)
        payload = {
            'amount': 450,
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        recipe_ingredient.refresh_from_db()
        self.assertNotEqual(recipe_ingredient.amount, payload['amount'])

    def test_delete_recipe_ingredient(self):
        """Test delete recipe ingredient."""
        recipe_ingredient = create_recipe_ingredient(
            recipe=self.recipe,
            ingredient=self.ingredient)
        url = detail_url(recipe_ingredient.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
