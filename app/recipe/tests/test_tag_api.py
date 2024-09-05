"""
Tests for TAG API endpoints.
"""

from django.test import TestCase

from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag
from recipe.serializers import TagSerializer
from recipe.helper_method import (
    create_user,
    create_tag
)

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Method to get the complete url for detail Tag."""
    return reverse('recipe:tag-detail', args=[tag_id])


class PublicTagApiTests(TestCase):
    """Tests for unauthenticated Tag API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        user = create_user(email='sarthak@example.com')
        create_tag(user=user, name="Guilty pleasure")
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    """Tests for authenticated TAG API Requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='akshat@example.com')
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieve tags is success."""

        create_tag(name='Chinese', user=self.user)
        create_tag(name='Vegetarian', user=self.user)
        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_detail_tag(self):
        """Test for getting detail tag info."""
        tag = create_tag(user=self.user, name='Chinese')
        url = detail_url(tag.id)

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, res.data['name'])

    def test_update_tag_success(self):
        """Test updating a tag is success."""
        tag = create_tag(user=self.user, name='Hawain Delicacy')
        url = detail_url(tag.id)

        payload = {
            'name': 'Thai Food',
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_create_new_tag(self):
        """Test creating a new tag."""
        payload = {
            'name': 'Vietanamese',
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

    def test_update_tag_not_created_by_user(self):
        """Test updating a tag, not created by user results error."""
        new_user = create_user(email='aman@example.com')
        tag = create_tag(user=new_user, name='Healthy')
        payload = {
            'name': 'Super Healthy',
        }
        url = detail_url(tag.id)

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        tag.refresh_from_db()
        self.assertNotEqual(tag.name, payload['name'])

    def test_delete_tag_not_created_by_user(self):
        """Test delete a tag, not created by user results error."""
        new_user = create_user(email='bhagwan@example.com')
        tag = create_tag(user=new_user, name='Healthy')
        url = detail_url(tag.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        tags = Tag.objects.filter(id=tag.id)
        self.assertTrue(tags.exists())

    def test_creating_tag_which_already_exists(self):
        """Test create tag which is already in system is unsuccessful."""
        tag = create_tag(user=self.user, name='Wonder Food')
        payload = {
            'name': 'Wonder Food',
        }
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        tag_count = Tag.objects.filter(name=tag.name).count()
        self.assertEqual(tag_count, 1)
