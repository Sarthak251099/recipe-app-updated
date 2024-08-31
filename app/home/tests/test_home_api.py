"""
Tests for home API.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Home
from home.serializers import HomeSerializer

HOME_URL = reverse('home:home-list')


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
        'parameters': '12876'
    }
    defaults.update(params)
    home = Home.objects.create(**defaults)
    return home


def detail_url(home_id):
    """Create the URL for detail home."""
    return reverse('home:home-detail', args=[home_id])


class PublicHomeAPITests(TestCase):
    """Tests for unauthenticated Home API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to fetch home."""
        create_home()
        res = self.client.get(HOME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateHomeApiTests(TestCase):
    """Tests for authenticated Home API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_home(self):
        """Tests retrieving home for authenticated user."""
        home = create_home()
        self.user.home = home
        self.user.save()

        res = self.client.get(HOME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = HomeSerializer(home)
        self.assertEqual(res.data[0], serializer.data)

    def test_create_home(self):
        """Test creating a home and assigning to user."""
        payload = {
            'name': 'Flat 320',
            'parameters': '129832',
        }
        res = self.client.post(HOME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        home = Home.objects.filter(id=res.data['id'])[0]
        self.assertEqual(home.name, payload['name'])
        self.assertEqual(home.parameters, payload['parameters'])
        self.assertEqual(self.user.home, home)

    def test_creating_multiple_homes(self):
        """Test creating multiple homes is unsuccessful."""
        home = create_home()
        self.user.home = home
        self.user.save()
        payload = {
            'name': 'Updated Home',
            'parameters': '12832',
        }
        res = self.client.post(HOME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(home.name, payload['name'])

    def test_updating_home_success(self):
        """Test updating home is success."""
        home = create_home()
        self.user.home = home
        self.user.save()
        payload = {
            'name': 'Updated Home',
            'parameters': '12832',
        }
        url = detail_url(home.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        home.refresh_from_db()
        self.assertEqual(home.name, payload['name'])
        self.assertEqual(home.parameters, payload['parameters'])
        self.assertEqual(self.user.home, home)

    def test_partially_updating_home_success(self):
        """Test partially updating home is success."""
        home = create_home()
        self.user.home = home
        self.user.save()
        payload = {
            'name': 'Updated Home',
        }
        url = detail_url(home.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        home.refresh_from_db()
        self.assertEqual(home.name, payload['name'])
        self.assertEqual(self.user.home, home)

    def test_updating_other_user_home_when_no_home(self):
        """Test updating home for different user when logged in
        user has no home assigned is unsuccessful."""

        home = create_home()
        new_user = create_user(
            email='test1@example.com',
            password='tarzan123',
            name='Aladdin',
        )
        new_user.home = home
        new_user.save()
        payload = {
            'name': 'Updated Home',
            'parameters': '12832',
        }
        url = detail_url(home.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        home.refresh_from_db()
        self.assertNotEqual(home.name, payload['name'])

    def test_deleting_home(self):
        """Test deleting home."""
        home = create_home()
        self.user.home = home
        self.user.save()
        url = detail_url(home.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Home.objects.filter(id=home.id).exists())
        self.user.refresh_from_db()
        self.assertEqual(self.user.home, None)

    def test_delete_home_for_different_user(self):
        """Test deleting home for different user is unsuccessfull."""
        new_user = create_user(
            email='user2@example.com',
            password='Pass1234'
        )
        home = create_home()
        new_user.home = home
        new_user.save()
        url = detail_url(home.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Home.objects.filter(id=home.id).exists())

    def test_update_other_user_home(self):
        """Test updating other user's home is unsuccessful when
        logged in user has a different home."""

        # logged in user has a home
        home = create_home(name='Banarasi Ghar')
        self.user.home = home
        self.user.save()

        # new user has another home
        new_user = create_user(
            email='user2@example.com',
        )
        new_home = create_home(name='Bihari Ghar')
        new_user.home = new_home
        new_user.save()

        payload = {
            'name': 'Updated Ghar',
        }

        # Logged in user trying to update new home of new user
        url = detail_url(new_home.id)
        self.client.patch(url, payload)
        self.assertEqual(new_user.home.name, 'Bihari Ghar')
