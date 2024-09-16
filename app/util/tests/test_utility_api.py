"""
Testcase for utility API requests.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from util.helper_method import (
    create_user,
    create_home,
    create_recipe,
    create_fav_recipe,
    add_to_inventory,
    create_ingredient,
    create_recipe_ingredient,
)
from datetime import datetime

SUGGEST_RECIPE_API = reverse('suggest-recipe')


class PrivateUtilityApiTests(TestCase):
    """Tests for utility functions API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='test@example.com', password='banana123')
        self.home = create_home()
        self.user.home = self.home
        self.user.save()
        self.client.force_authenticate(self.user)

    def test_suggest_recipe_when_no_recipe_in_system(self):
        """Test suggest recipe request when no recipe in system."""
        res = self.client.get(SUGGEST_RECIPE_API)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_suggest_recipe(self):
        """Test suggest recipe when recipes in system."""

        """
        Butter Paneer - Requires Butter(150), Paneer(200), Cooked on 2/9/24.
        Available - Butter(200), Paneer(200)
        Verdict - Should be cooked

        Poha - Requires Onion(250), Cooked on 6/9/2024.
        Available - Onion(0)
        Verdict - Cannot

        Bhindi - Requires Okra(350), Onion(150), Cooked 12/9/24.
        Available - Okra(300), Onion(0)
        Verdict - Cannot
        """

        # setting up recipes

        recipe1 = create_recipe(user=self.user, title='Butter Paneer')
        recipe2 = create_recipe(user=self.user, title='Poha')
        recipe3 = create_recipe(user=self.user, title='Bhindi')

        # creating few ingredients

        ing1 = create_ingredient(user=self.user, name='Butter')
        ing2 = create_ingredient(user=self.user, name='Okra')
        ing3 = create_ingredient(user=self.user, name='Paneer')
        ing4 = create_ingredient(user=self.user, name='Onion')

        # create recipe ingredients requirement for cooking

        create_recipe_ingredient(recipe=recipe1, ingredient=ing1, amount=150)
        create_recipe_ingredient(recipe=recipe1, ingredient=ing3, amount=200)
        create_recipe_ingredient(recipe=recipe2, ingredient=ing4, amount=250)
        create_recipe_ingredient(recipe=recipe3, ingredient=ing2, amount=350)
        create_recipe_ingredient(recipe=recipe3, ingredient=ing4, amount=150)

        # creating inventory for home

        add_to_inventory(home=self.home, ingredient=ing1, amount=200)
        add_to_inventory(home=self.home, ingredient=ing2, amount=300)
        add_to_inventory(home=self.home, ingredient=ing3, amount=200)

        # create fav recipes for a home

        date1 = datetime.strptime('02-09-2024', '%d-%m-%Y').date()
        date2 = datetime.strptime('06-09-2024', '%d-%m-%Y').date()
        date3 = datetime.strptime('12-09-2024', '%d-%m-%Y').date()

        create_fav_recipe(home=self.home, recipe=recipe1, last_cooked=date1)
        create_fav_recipe(home=self.home, recipe=recipe2, last_cooked=date2)
        create_fav_recipe(home=self.home, recipe=recipe3, last_cooked=date3)

        res = self.client.get(SUGGEST_RECIPE_API)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['recipe'], recipe1.id)

    def test_suggest_recipe2(self):
        """Test suggest recipe when recipes in system test 2."""

        """
        Butter Paneer - Requires Butter(150), Paneer(200), Cooked on 2/9/24.
        Available - Butter(200), Paneer(200)
        Verdict - Should be cooked.

        Poha - Requires Onion(100), Cooked on 6/9/2024.
        Available - Onion(200)
        Verdict - Can be cooked, but more recent.

        Bhindi - Requires Okra(350), Onion(150), Cooked 12/9/24.
        Available - Okra(300), Onion(200)
        Verdict - Cannot
        """

        # setting up recipes

        recipe1 = create_recipe(user=self.user, title='Butter Paneer')
        recipe2 = create_recipe(user=self.user, title='Poha')
        recipe3 = create_recipe(user=self.user, title='Bhindi')

        # creating few ingredients

        ing1 = create_ingredient(user=self.user, name='Butter')
        ing2 = create_ingredient(user=self.user, name='Okra')
        ing3 = create_ingredient(user=self.user, name='Paneer')
        ing4 = create_ingredient(user=self.user, name='Onion')

        # create recipe ingredients requirement for cooking

        create_recipe_ingredient(recipe=recipe1, ingredient=ing1, amount=150)
        create_recipe_ingredient(recipe=recipe1, ingredient=ing3, amount=200)
        create_recipe_ingredient(recipe=recipe2, ingredient=ing4, amount=100)
        create_recipe_ingredient(recipe=recipe3, ingredient=ing2, amount=350)
        create_recipe_ingredient(recipe=recipe3, ingredient=ing4, amount=150)

        # creating inventory for home

        add_to_inventory(home=self.home, ingredient=ing1, amount=200)
        add_to_inventory(home=self.home, ingredient=ing2, amount=300)
        add_to_inventory(home=self.home, ingredient=ing3, amount=200)
        add_to_inventory(home=self.home, ingredient=ing4, amount=200)

        # create fav recipes for a home

        date1 = datetime.strptime('02-09-2024', '%d-%m-%Y').date()
        date2 = datetime.strptime('06-09-2024', '%d-%m-%Y').date()
        date3 = datetime.strptime('12-09-2024', '%d-%m-%Y').date()

        create_fav_recipe(home=self.home, recipe=recipe1, last_cooked=date1)
        create_fav_recipe(home=self.home, recipe=recipe2, last_cooked=date2)
        create_fav_recipe(home=self.home, recipe=recipe3, last_cooked=date3)

        res = self.client.get(SUGGEST_RECIPE_API)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['recipe'], recipe1.id)
