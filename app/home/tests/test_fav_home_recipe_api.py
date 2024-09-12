"""
Test API requests for favourite home recipes.
"""

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
# from datetime import datetime
from core.models import FavHomeRecipe
from home.serializers import FavHomeRecipeSerializer
from home.helper_method import (
    create_user,
    create_home,
    create_recipe,
    create_fav_recipe,
)

FAV_HOME_RECIPE_URL = reverse('home:fav-recipes')
# FAV_HOME_RECIPE_CREATE_URL = reverse('home:fav-recipe-create')


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

    # def test_add_fav_recipe_for_user_home(self):
    #     """Test add a new recipe in fav recipe for authenticated
    #     user's home."""
    #     date = datetime.strptime('12-09-2023', '%d-%m-%Y').date()
    #     recipe = create_recipe(user=self.user, title='Bhature')
    #     payload = {
    #         'recipe': 5,
    #     }
    #     res = self.client.post(FAV_HOME_RECIPE_CREATE_URL, payload=payload)
    #     self.assertEqual(res.data, status.HTTP_201_CREATED)
