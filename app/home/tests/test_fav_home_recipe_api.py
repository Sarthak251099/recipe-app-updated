"""
Test API requests for favourite home recipes.
"""

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from datetime import datetime
from core.models import FavHomeRecipe
from home.serializers import FavHomeRecipeSerializer
from home.helper_method import (
    create_user,
    create_home,
    create_recipe,
    create_fav_recipe,
)

FAV_HOME_RECIPE_URL = reverse('home:fav-recipes')
FAV_HOME_RECIPE_CREATE_URL = reverse('home:fav-recipe-create')


def detail_url(fav_recipe_id):
    return reverse('home:fav-recipe-update', args=[fav_recipe_id])


class PublicFavHomeRecipeTests(TestCase):
    """Test for Favourite home recipes."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_api_request(self):
        """Test unauthenticated Fav home recipe request."""
        res = self.client.get(FAV_HOME_RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateFavHomeRecipeTests(TestCase):
    """Test for favourite home recipes."""

    def setUp(self):
        self.client = APIClient()
        self.home = create_home()
        self.user = create_user(email='user@example.com', password='Test123')
        self.user.home = self.home
        self.user.save()
        self.recipe = create_recipe(user=self.user)
        self.client.force_authenticate(self.user)

    def test_fetch_fav_recipes_for_user_home(self):
        """Test fetch favourite recipes for auth user's home."""
        create_fav_recipe(home=self.home, recipe=self.recipe)
        res = self.client.get(FAV_HOME_RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        fav_recipe = FavHomeRecipe.objects.filter(home=self.home)
        serializer = FavHomeRecipeSerializer(fav_recipe, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_fetch_fav_recipe_limited_to_user_home(self):
        """Test fetch fav recipe is limited to user's home."""
        create_fav_recipe(home=self.home, recipe=self.recipe)
        new_home = create_home(name='New Home')
        create_fav_recipe(home=new_home, recipe=self.recipe)

        res = self.client.get(FAV_HOME_RECIPE_URL)
        fav_recipe = FavHomeRecipe.objects.filter(home=self.home)
        serializer = FavHomeRecipeSerializer(fav_recipe, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_add_fav_recipe_for_user_home(self):
        """Test add a new recipe in fav recipe for authenticated
        user's home."""
        date = datetime.strptime('12-09-2023', '%d-%m-%Y').date()
        recipe = create_recipe(user=self.user, title='Bhature')
        payload = {
            'recipe': recipe.id,
            'date': date,
            'rating': 3,
        }
        res = self.client.post(FAV_HOME_RECIPE_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_add_fav_recipe_when_recipe_already_fav(self):
        """Test add a fav recipe when recipe is already in favourites
        for the authenticated user's home."""
        recipe = create_recipe(user=self.user, title='Chole')
        create_fav_recipe(home=self.home, recipe=recipe)
        payload = {
            'recipe': recipe.id,
            'rating': 7,
        }
        res = self.client.post(FAV_HOME_RECIPE_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        fav_recipe = FavHomeRecipe.objects.filter(
            recipe=recipe,
            home=self.home,
        ).count()
        self.assertEqual(fav_recipe, 1)

    def test_add_fav_recipe_when_recipe_not_exist(self):
        """Test adding a recipe when recipe does not exist."""
        payload = {
            'recipe': 1000,
            'rating': 7,
        }
        res = self.client.post(FAV_HOME_RECIPE_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_fav_recipe(self):
        """Test update fav recipe for user's home."""
        recipe = create_recipe(user=self.user, title='Chole')
        fav_recipe = create_fav_recipe(home=self.home, recipe=recipe)
        payload = {
            'rating': 3,
        }
        url = detail_url(fav_recipe.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        fav_recipe.refresh_from_db()
        self.assertEqual(fav_recipe.rating, payload['rating'])

    def test_update_fav_recipe_for_other_home(self):
        """Test updating fav recipe for other home."""
        new_home = create_home(name='New Home')
        fav_recipe = create_fav_recipe(home=new_home, recipe=self.recipe)
        payload = {
            'rating': 3,
        }
        url = detail_url(fav_recipe.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_fav_recipe(self):
        """Test deleting fav recipe."""
        fav_recipe = create_fav_recipe(home=self.home, recipe=self.recipe)
        url = detail_url(fav_recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
