"""
Tests for TAG API endpoints.
"""

from django.test import TestCase

from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag
from django.contrib.auth import get_user_model
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def create_user(**params):
    defaults = {
        'email': 'test123@example.com',
        'password': 'testpass123'
    }
    defaults.update(params)
    user = get_user_model().objects.create_user(**defaults)
    return user


def create_tag(user, **params):
    defaults = {
        'name': 'Tag 1'
    }
    defaults.update(params)
    tag = Tag.objects.create(user=user, **defaults)

    return tag


def detail_url(tag_id):
    """Method to get the complete url for detail Tag."""
    return reverse('recipe:tag-detail', args=[tag_id])


class PublicTagApiTests(TestCase):
    """Tests for unauthenticated Tag API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        user = create_user()
        create_tag(user=user)
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    """Tests for authenticated TAG API Requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieve tags returns success."""

        create_tag(name='Chinese', user=self.user)
        create_tag(name='Vegetarian', user=self.user)
        res = self.client.get(TAGS_URL)
        tags = Tag.objects.filter(user=self.user)
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tag_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Fruity')
        tag = create_tag(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_get_detail_tag(self):
        """Test for getting detail tag info."""
        tag = create_tag(user=self.user)
        url = detail_url(tag.id)

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, res.data['name'])

    def test_update_tag_success(self):
        """Test updating a tag is success."""
        tag = create_tag(user=self.user, name='Hawain Delicacy')
        url = detail_url(tag.id)

        payload = {
            'name': 'Thai Food'
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_create_new_tag(self):
        """Tests creating a new tag."""
        payload = {
            'name': 'Vietanamese'
        }
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tag = Tag.objects.get(id=res.data['id'])
        self.assertEqual(tag.name, payload['name'])
        self.assertEqual(tag.user, self.user)

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = create_tag(user=self.user, name='Breakfast')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())
