"""
Tests for `recipe` APIs.
"""
import os
import tempfile
from PIL import Image
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPES_URL = reverse('recipe:recipe-list')


def get_recipe_detail_url(idx):
    return reverse('recipe:recipe-detail', args=[idx])


def get_img_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


# Helper function to create recipe
def create_recipe(user, **params):
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 22,
        'cost': Decimal('3.49'),
        'description': 'Easy Peasy',
        'link': 'https://duckduckgo.com/'
    }

    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUP(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test only authenticated requests are allowed."""
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedRecipeAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email='user1@example.com', password='Whatever!'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test authenticated user can access their recipes."""
        # Create a bunch of recipes:
        for i in range(3):
            _ = create_recipe(user=self.user, title=f'Recipe {i}')

        res = self.client.get(RECIPES_URL)

        recipes_fetched = Recipe.objects.all().order_by('-id')
        # many=True forces to have returned a list of items, even if it's jsut 1.
        serializer = RecipeSerializer(recipes_fetched, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test user can only access their own created recipes."""
        # Create another user & a recipe for that user.
        user2 = get_user_model().objects.create_user(
            email='not_user1@example.com', password='NotUser1'
        )
        # Now create a recipe for user2, and another recipe for our default user, `user1`
        _ = create_recipe(user=user2)
        _ = create_recipe(user=self.user)  # user defined in `setUp`

        # fetch the recipes from the API:
        res = self.client.get(RECIPES_URL)  # we authenticated user1 in setUp

        # Fetch the recipies for user1 from DB
        recipes_fetched_user1 = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes_fetched_user1, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        recipe = create_recipe(user=self.user)

        recipe_url = get_recipe_detail_url(recipe.id)
        res = self.client.get(recipe_url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""
        recipe_payload = {
            'title': 'Random Recipe',
            'time_minutes': 10,
            'cost': Decimal('7.99')
        }

        res = self.client.post(RECIPES_URL, recipe_payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        # Make sure values match between the recipe saved in DB & the one returned from URL:
        for k, v in recipe_payload.items():
            self.assertEqual(getattr(recipe, k), v)
        # Also make sure the assigned user to the recipe is the authenticated user.
        self.assertEqual(recipe.user, self.user)

    def test_create_recipe_with_new_tags(self):
        payload = {
            'title': 'Vejetable Taj Mahal',
            'time_minutes': 30,
            'cost': Decimal(13.5),
            'tags': [{'name': 'Indian'}, {'name': 'Vegi'}]
        }
        # Because we're passing nested objects (the `tags` value),
        # we pass `format=json` to make sure it'll get converted correctly.
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes_fetched = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes_fetched.count(), 1)  # we created 1 recipe

        recipe = recipes_fetched[0]
        self.assertEqual(recipe.tags.count(), 2)  # 2 tags is assigned to the recipe
        for tag in payload['tags']:
            recipe_tag = recipe.tags.filter(name=tag['name'], user=self.user)
            self.assertTrue(recipe_tag.exists())

    def test_create_recipe_with_existing_tags(self):
        """Test cannot add the same tag to the recipe multiple times."""
        tag_already_created = Tag.objects.create(user=self.user, name='old-tag')
        payload = {
            'title': 'Recipe Title',
            'time_minutes': 1,
            'cost': Decimal('9.99'),
            'tags': [{'name': 'Indian'}, {'name': 'old-tag'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)  # we created 1 recipe above

        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)  # the recipe should have 2 tags assigned
        self.assertIn(tag_already_created, recipe.tags.all())
        for tag in payload['tags']:
            recipe_tag = recipe.tags.filter(name=tag['name'], user=self.user)
            self.assertTrue(recipe_tag.exists())

    def test_create_tag_on_update_recipe(self):
        """Test."""
        recipe = create_recipe(user=self.user)
        recipe_url = get_recipe_detail_url(recipe.id)

        payload = {'tags': [{'name': 'Lunch'}]}
        res = self.client.patch(recipe_url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag = Tag.objects.get(user=self.user, name=payload['tags'][0]['name'])
        self.assertIn(tag, recipe.tags.all())

    def test_modify_tag_on_update_recipe(self):
        """Test."""
        tag1 = Tag.objects.create(user=self.user, name='tag1')
        tag2 = Tag.objects.create(user=self.user, name='tag2')

        # Create a recipe & add `tag1` to it:
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag1)
        recipe_url = get_recipe_detail_url(recipe.id)

        # Update the recipe with a new tag, `tag2`:
        payload = {'tags': [{'name': 'tag2'}]}
        res = self.client.patch(recipe_url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag2, recipe.tags.all())  # tag2 should belong to recipe
        self.assertNotIn(tag1, recipe.tags.all())  # we've removed tag1 from recipe

    def test_clear_recipe_tags(self):
        """Test."""
        recipe = create_recipe(user=self.user)
        recipe_url = get_recipe_detail_url(recipe.id)
        # Add a couple of tags to the recipe:
        for i in range(3):
            tag = Tag.objects.create(user=self.user, name=f'tag-{i}')
            recipe.tags.add(tag)

        # Remove the assigned tags.
        payload = {'tags': []}
        res = self.client.patch(recipe_url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)  # we've cleared all the tags

    def test_create_recipe_with_new_ingredients(self):
        payload = {
            'title': 'chicken curry',
            'time_minutes': 45,
            'cost': Decimal('13.5'),
            'ingredients': [{'name': 'Coconut milk'}, {'name': 'Curry powder'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes_fetched = Recipe.objects.filter(user=self.user)  # 1 recipe is available
        self.assertEqual(recipes_fetched.count(), 1)

        recipe = recipes_fetched[0]
        self.assertEqual(recipe.ingredients.count(), 2)  # recipe payload has 2 ingredients
        for itm in payload['ingredients']:
            ingredient = recipe.ingredients.filter(user=self.user, name=itm['name'])
            self.assertTrue(ingredient.exists())

    def test_create_recipe_with_existing_ingredients(self):
        """
        Test duplicates are recorded once.
        NOTE: some tests are ommitted as they're very similar to the tests in
        `test_create_recipe_with_new_ingredients`.
        """
        ingredient_0 = Ingredient.objects.create(user=self.user, name='Curry powder')
        payload = {
            'title': 'chicken curry',
            'time_minutes': 45,
            'cost': Decimal('13.5'),
            'ingredients': [{'name': 'Coconut milk'}, {'name': 'Curry powder'}]
        }
        _ = self.client.post(RECIPES_URL, payload, format='json')
        recipes_fetched = Recipe.objects.filter(user=self.user)
        recipe = recipes_fetched[0]
        # Check if the already created recipe is in the ingredients list of recipe:
        self.assertIn(ingredient_0, recipe.ingredients.all())
        # Make sure the ingredient is not duplicated, duplicates are recorded only once:
        self.assertEqual(recipe.ingredients.count(), 2)

    def test_create_ingredient_on_update_recipe(self):
        """Test."""
        recipe = create_recipe(user=self.user)
        recipe_url = get_recipe_detail_url(recipe.id)

        payload = {'ingredients': [{'name': 'Salt'}]}
        res = self.client.patch(recipe_url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient_name = payload['ingredients'][0]['name']
        ingredient = Ingredient.objects.get(user=self.user, name=ingredient_name)
        self.assertIn(ingredient, recipe.ingredients.all())

    def test_modify_ingredient_on_update_recipe(self):
        """Test."""
        ingredient1 = Ingredient.objects.create(user=self.user, name='ingredient-1')
        ingredient2 = Ingredient.objects.create(user=self.user, name='ingredient-2')

        # Create a recipe & add `tag1` to it:
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)
        recipe_url = get_recipe_detail_url(recipe.id)

        # Update the recipe with a new tag, `tag2`:
        payload = {'ingredients': [{'name': 'ingredient-2'}]}
        res = self.client.patch(recipe_url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # ingredient1 was removed from recipe& ingredient2 should belong to recipe
        self.assertNotIn(ingredient1, recipe.ingredients.all())
        self.assertIn(ingredient2, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test."""
        recipe = create_recipe(user=self.user)
        recipe_url = get_recipe_detail_url(recipe.id)
        # Add a couple of tags to the recipe:
        for i in range(3):
            ingredient = Ingredient.objects.create(user=self.user, name=f'ingredient-{i}')
            recipe.ingredients.add(ingredient)

        # Remove the assigned tags.
        payload = {'ingredients': []}
        res = self.client.patch(recipe_url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)  # we've cleared all the ingredients


# Test for Img -------------------------------------------------- #
class ImageUploadTests(TestCase):
    """Tests for the image upload API."""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user1@example.com', password='Whatever!'
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        """Remove images created during test."""
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a recipe."""
        img_url = get_img_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as img_file:
            img_obj = Image.new('RGB', (10, 10))
            img_obj.save(img_file, format='JPEG')  # Save the data to disk.
            img_file.seek(0)
            payload = {'image': img_file}
            res = self.client.post(img_url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading invalid image."""
        img_url = get_img_upload_url(self.recipe.id)
        payload = {'image': 'not_an_image'}
        res = self.client.post(img_url, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
