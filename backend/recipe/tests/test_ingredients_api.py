"""
Test for the **ingredient** api.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(payload={}):
    default = {'email': 'user@example.com', 'password': 'Whatever!'}
    default.update(payload)
    user = get_user_model().objects.create_user(**default)
    return user


class PublicIngredientsAPITests(TestCase):
    """Test unauthenticated API requests."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test only authenticated requests get response."""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedIngredientsAPITests(TestCase):
    """Test authenticated API requests."""
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving ingredients for the user."""
        for ingredient in ['salt', 'cheese', 'pepper']:
            _ = Ingredient.objects.create(user=self.user, name=ingredient)

        res = self.client.get(INGREDIENTS_URL)

        # Fetch the created tags from DB:
        ingredients_fetched = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients_fetched, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test ingredients are assigned and retrieved for the authenticated user only."""
        user2 = create_user({'email': 'not_user1@example.com'})  # create a 2nd user
        _ = Ingredient.objects.create(user=user2, name='Ingredient-2')

        # Create a tag for the authenticated user:
        ingredient1 = Ingredient.objects.create(user=self.user, name='Ingredient-1')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient1.name)
        self.assertEqual(res.data[0]['id'], ingredient1.id)
