"""
Tests for the **tags** api.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def create_user(payload={}):
    default = {'email': 'user@example.com', 'password': 'Whatever!'}
    default.update(payload)
    user = get_user_model().objects.create_user(**default)
    return user


class PublicTagsAPITests(TestCase):
    """Test unauthenticated API requests."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test only authenticated requests get response."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTagsAPITests(TestCase):
    """Test authenticated API requests."""
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags for the user."""
        for tag in ['Vegan', 'Dessert', 'Oriental']:
            _ = Tag.objects.create(user=self.user, name=tag)

        res = self.client.get(TAGS_URL)

        # Fetch the created tags from DB:
        tags_fetched = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags_fetched, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test tags are assigned and retrieved for the authenticated user only."""
        user2 = create_user({'email': 'not_user1@example.com'})
        _ = Tag.objects.create(user=user2, name='tag-created-by-user2')

        # Create a tag for the authenticated user:
        tag_user1 = Tag.objects.create(user=self.user, name='tag1')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag_user1.name)
        self.assertEqual(res.data[0]['id'], tag_user1.id)
