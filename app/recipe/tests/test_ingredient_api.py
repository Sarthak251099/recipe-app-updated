"""
Tests for ingredients API requests.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Ingredient

from rest_framework import status
from rest_framework.test import APIClient
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(**params):
    defaults = {
        'email': 'test123@example.com',
        'password': 'testpass123'
    }
    defaults.update(params)
    user = get_user_model().objects.create_user(**defaults)
    return user


def create_ingredient(user, **params):
    defaults = {
        'name': 'Wheat'
    }
    defaults.update(params)
    ingredient = Ingredient.objects.create(user=user, **defaults)

    return ingredient


class PublicIngredientApiTests(TestCase):
    """Tests for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth required for retrieving ingredient."""
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Tests for authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_get_ingredients_successful(self):
        """Test retrieve ingredients returns success."""

        create_ingredient(name='Salt', user=self.user)
        create_ingredient(name='Pasta', user=self.user)
        res = self.client.get(INGREDIENT_URL)
        ing = Ingredient.objects.all().order_by('name')
        serializer = IngredientSerializer(ing, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_detail_ingredient(self):
        """Test fetching detail ingredient info."""
        ingredient = create_ingredient(name='Pepper', user=self.user)
        url = detail_url(ingredient.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = IngredientSerializer(ingredient)
        self.assertEqual(serializer.data, res.data)

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        ingredient = create_ingredient(name='Garam Masala', user=self.user)
        url = detail_url(ingredient.id)
        payload = {
            'name': 'Raita Masala',
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_create_new_ingredient(self):
        """Test creating a new ingredient is success."""
        payload = {
            'name': 'Jeeravan',
        }
        res = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = Ingredient.objects.filter(name='Jeeravan', user=self.user)
        self.assertTrue(exists.exists())

    def test_delete_ingredient(self):
        """Test deleting a ingredient."""
        ing = create_ingredient(user=self.user, name='Baking Powder')

        url = detail_url(ing.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ings = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ings.exists())

    def test_update_ingredient_not_created_by_user(self):
        """Test updating an ingredient, not created by user fails."""
        new_user = create_user(email='aman@example.com')
        ing = create_ingredient(user=new_user, name='Garam Masala')
        payload = {
            'name': 'Super Garam Masala',
        }
        url = detail_url(ing.id)

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        ing.refresh_from_db()
        self.assertNotEqual(ing.name, payload['name'])

    def test_delete_ingredient_not_created_by_user(self):
        """Test delete ingredient, not created by user fails."""
        new_user = create_user(email='bhagwan@example.com')
        ing = create_ingredient(user=new_user, name='Garam Masala')
        url = detail_url(ing.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        ings = Ingredient.objects.filter(id=ing.id)
        self.assertTrue(ings.exists())
