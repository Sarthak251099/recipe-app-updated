"""
Tests for inventory API requests.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import (
    Home,
    Inventory,
    Ingredient,
)
from django.contrib.auth import get_user_model
from inventory.serializers import InventorySerializer

INVENTORY_URL = reverse('inventory:inventory-list')


def add_to_inventory(home, ingredient, amount=500):
    """Add ingredient item to inventory of home."""
    return Inventory.objects.create(
        home=home,
        ingredient=ingredient,
        amount=amount
        )


def create_user(**params):
    """Create and return a user."""
    defaults = {
        'name': 'Akshat',
        'email': 'test@example.com',
        'password': 'Akshat112',
    }
    defaults.update(params)
    user = get_user_model().objects.create_user(**defaults)
    return user


def create_home(**params):
    """Create and return a new home."""
    defaults = {
        'name': 'Oaklites',
        'parameters': '12876',
    }
    defaults.update(params)
    home = Home.objects.create(**defaults)
    return home


def create_ingredient(user, **params):
    defaults = {
        'name': 'Wheat'
    }
    defaults.update(params)
    ingredient = Ingredient.objects.create(user=user, **defaults)

    return ingredient


class PublicInventoryApiTests(TestCase):
    """Tests for unauthenticated inventory API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test unauthenticated API request."""
        user = create_user()
        ingredient = create_ingredient(user=user)
        home = create_home()
        add_to_inventory(home=home, ingredient=ingredient)
        res = self.client.get(INVENTORY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateInventoryApiTests(TestCase):
    """Tests for authenticated inventory API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.home = create_home()
        self.client.force_authenticate(self.user)

    def test_fetch_inventory_for_home(self):
        """Tests for fetching ingredient list for a home."""
        self.user.home = self.home
        self.user.save()
        ingredient = create_ingredient(user=self.user, name='Pepper')
        add_to_inventory(home=self.home, ingredient=ingredient)
        add_to_inventory(home=self.home, ingredient=ingredient)

        res = self.client.get(INVENTORY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        inventory = Inventory.objects.filter(home=self.home).order_by('-id')
        serializer = InventorySerializer(inventory, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_fetch_inventory_for_user_without_home(self):
        """Tests fetching ingredient list when user has no home."""
        res = self.client.get(INVENTORY_URL)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inventory_object(self):
        """Tests creating an inventory object for a home."""
        self.user.home = self.home
        self.user.save()
        ingredient = create_ingredient(user=self.user, name='Dhaniya')
        payload = {
            'home': self.home.id,
            'ingredient': ingredient.id,
            'amount': 300,
        }
        res = self.client.post(INVENTORY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        inventory = Inventory.objects.get(home=self.home)
        serializer = InventorySerializer(inventory)
        self.assertEqual(serializer.data, res.data)
