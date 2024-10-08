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


def detail_url(inventory_id):
    """Return URL for updating inventory object."""
    return reverse('home:inventory-detail', args=[inventory_id])


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
        ingredient2 = create_ingredient(user=self.user, name='Brocoli')
        add_to_inventory(home=self.home, ingredient=ingredient)
        add_to_inventory(home=self.home, ingredient=ingredient2)

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
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_inventory_limited_to_user_home(self):
        """Test retrieve inventory list limited to user's home"""
        ing1 = create_ingredient(user=self.user, name='Pudina')
        ing2 = create_ingredient(user=self.user, name='Garlic')
        new_home = create_home(name="New Home")
        add_to_inventory(home=self.home, ingredient=ing1)
        add_to_inventory(home=new_home, ingredient=ing2)

        res = self.client.get(FETCH_INVENTORY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        inv = Inventory.objects.filter(home=self.home).order_by('-id')
        serializer = InventorySerializer(inv, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_create_inventory_for_home(self):
        """Test creating inventory for user's home."""
        ingredient = create_ingredient(user=self.user, name='Dhaniya')
        payload = {
            'ingredient': ingredient.id,
            'amount': 300,
        }
        res = self.client.post(CREATE_INVENTORY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        inventory = Inventory.objects.get(home=self.home)
        serializer = InventorySerializer(inventory)
        self.assertEqual(serializer.data, res.data)

    def test_create_when_ingredient_already_in_inventory(self):
        """Test create inventory when ingredient already in inventory."""
        ingredient = create_ingredient(user=self.user, name='Dhaniya')
        add_to_inventory(home=self.home, ingredient=ingredient)
        payload = {
            'ingredient': ingredient.id,
            'amount': 300,
        }
        res = self.client.post(CREATE_INVENTORY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inventory_for_ingredient_not_available(self):
        """Test create inventory for ingredient which is unavailable."""
        payload = {
            'ingredient': 100000,
            'amount': 300,
        }
        res = self.client.post(CREATE_INVENTORY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_inventory_for_user_home(self):
        """Test update inventory for user's home."""
        ingredient = create_ingredient(user=self.user, name='Ketchup')
        inventory = add_to_inventory(home=self.home, ingredient=ingredient)
        url = detail_url(inventory.id)
        payload = {
            'amount': 100,
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        inventory.refresh_from_db()
        self.assertEqual(inventory.amount, payload['amount'])

    def test_update_inventory_ingredient_which_already_exists(self):
        """Test updating inventory item with ingredient that already
        exists in the inventory for the home is unsuccessful."""

        # Creating inventory items ketchup and banana
        ing1 = create_ingredient(user=self.user, name='Ketchup')
        inv1 = add_to_inventory(home=self.home, ingredient=ing1)

        ing2 = create_ingredient(user=self.user, name='Banana')
        add_to_inventory(home=self.home, ingredient=ing2)

        # Payload for changing Ketchup ingredient to banana ing.
        url = detail_url(inv1.id)
        payload = {
            'ingredient': ing2.id,
        }

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_updating_home_in_inventory_for_user_unsuccessful(self):
        """Test update home in inventory for a user is unsuccessful."""
        new_home = create_home(name='New Home')
        ingredient = create_ingredient(user=self.user, name='Ketchup')
        inventory = add_to_inventory(home=self.home, ingredient=ingredient)
        url = detail_url(inventory.id)
        payload = {
            'home': new_home.id,
        }
        self.client.patch(url, payload)
        inventory.refresh_from_db()
        self.assertNotEqual(inventory.home.id, payload['home'])

    def test_updating_inventory_for_different_home_fails(self):
        """Test update inventory for a home which is not the
        authenticated user's home, results unsuccessful."""

        new_home = create_home(name='New Home')
        ingredient = create_ingredient(user=self.user, name='Salsa')
        inventory = add_to_inventory(home=new_home, ingredient=ingredient)
        url = detail_url(inventory.id)
        payload = {
            'amount': 2000,
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        inventory.refresh_from_db()
        self.assertNotEqual(inventory.amount, payload['amount'])

    def test_update_inventory_with_ingredient_not_available(self):
        """Test updating inventory with ingredient which is
        not available in the system is unsuccessful."""

        ingredient = create_ingredient(user=self.user, name='Jeeravan')
        inventory = add_to_inventory(home=self.home, ingredient=ingredient)
        url = detail_url(inventory.id)
        payload = {
            'ingredient': 200,
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        inventory.refresh_from_db()
        self.assertNotEqual(inventory.ingredient.id, payload['ingredient'])

    def test_delete_inventory_item(self):
        """Test deleting inventory item is success."""

        ingredient = create_ingredient(user=self.user, name='Jeeravan')
        inventory = add_to_inventory(home=self.home, ingredient=ingredient)
        url = detail_url(inventory.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        inv = Inventory.objects.filter(id=inventory.id)
        self.assertFalse(inv.exists())

    def test_delete_inventory_for_different_home(self):
        """Test delete inventory item for home which is
        not authenticated user's home is unsuccessful."""
        new_home = create_home(name='New Home')
        ingredient = create_ingredient(user=self.user, name='Banana')
        inventory = add_to_inventory(home=new_home, ingredient=ingredient)
        url = detail_url(inventory.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
