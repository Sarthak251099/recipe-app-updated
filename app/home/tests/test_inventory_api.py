"""
Tests for inventory API requests.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import (
    Inventory,
)
from home.serializers import InventorySerializer
from home.helper_method import (
    create_user,
    create_ingredient,
    create_home,
    add_to_inventory,
)

CREATE_INVENTORY_URL = reverse('home:inventory-create')
FETCH_INVENTORY_URL = reverse('home:inventory-fetch')


class PublicInventoryApiTests(TestCase):
    """Test unauthenticated Inventory API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_fetch_inventory_for_home(self):
        """Test fetching inventory list is unsuccessful."""

        res = self.client.get(FETCH_INVENTORY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateInventoryAPiTests(TestCase):
    """Test Inventory API requests authentciated."""

    def setUp(self):
        self.client = APIClient()
        self.home = create_home()
        self.user = create_user(email='user@example.com', password='Test123')
        self.user.home = self.home
        self.user.save()
        self.client.force_authenticate(self.user)

    def test_fetching_inventory_list_for_user_home(self):
        """Test fetch inventory for user's home."""
        ingredient = create_ingredient(user=self.user, name='Pepper')
        add_to_inventory(home=self.home, ingredient=ingredient)
        res = self.client.get(FETCH_INVENTORY_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        inventory = Inventory.objects.filter(home=self.home).order_by('-id')
        serializer = InventorySerializer(inventory, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_fetch_inventory_for_user_without_home(self):
        """Tests fetching inventory list when user has no home."""
        self.home.delete()
        self.user.refresh_from_db()
        res = self.client.get(FETCH_INVENTORY_URL)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inventory_for_home(self):
        """Test creating inventory for user's home."""
        ingredient = create_ingredient(user=self.user, name='Dhaniya')
        payload = {
            'home': self.home.id,
            'ingredient': ingredient.id,
            'amount': 300,
        }
        res = self.client.post(CREATE_INVENTORY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        inventory = Inventory.objects.get(home=self.home)
        serializer = InventorySerializer(inventory)
        self.assertEqual(serializer.data, res.data)

    def test_create_inventory_for_different_home_is_fail(self):
        """Test create inventory for a home which is not the
        logged in user's home is unsuccessful."""

        new_home = create_home(name='New Home')
        ingredient = create_ingredient(user=self.user, name='Dhaniya')
        payload = {
            'home': new_home.id,
            'ingredient': ingredient.id,
            'amount': 300,
        }

        res = self.client.post(CREATE_INVENTORY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
