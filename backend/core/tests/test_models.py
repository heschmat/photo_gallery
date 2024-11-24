"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from decimal import Decimal

from core import models


def create_user(payload={}):
    default = {'email': 'userX@example.com', 'password': 'DefaultUser'}
    default.update(payload)
    return get_user_model().objects.create_user(**default)


class ModelTests(TestCase):
    """Test Models."""

    def test_create_user_with_email_ok(self):
        email = "user@example.com"
        password = 'Whatever1'
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        # We don't save the actuall pass; hence, we check if the hashes match.
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        sample_emails = (
            'test1@EXAMPLE.com', 'Test2@Example.com', 'TEST3@EXAMPLE.COM', 'test4@example.COM'
        )

        for email in sample_emails:
            user, domain = email.split('@')
            email_normalized = user + '@' + domain.lower()
            user = get_user_model().objects.create_user(email=email, password='Whatever1')
            self.assertEqual(user.email, email_normalized)

    def test_new_user_without_email_raises_err(self):
        """User must provide email upon registration; otherwise ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'Whatever1')

    def test_create_superuser_with_email_ok(self):
        user = get_user_model().objects.create_superuser(
            email='admin@example.com', password='JeSuisSuperUser'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    # Tests for Recipe Model --------------------------------------- #
    def test_create_recipe_ok(self):
        """Test user can create a recipe successfully."""
        test_user = get_user_model().objects.create_user(
            email='user1@example.com', password='Whatever!'
        )

        sample_recipe = models.Recipe.objects.create(
            user=test_user,
            title='A Sample Recipe',
            time_minutes=5,
            cost=Decimal('4.99'),
            description='The most delicious snack you\'ve ever had',
        )

        self.assertEqual(str(sample_recipe), sample_recipe.title)

    def test_create_tag(self):
        """Test creating a tag is successful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='tag-1')

        # Make sure tag is created & with correct representation.
        self.assertEqual(str(tag), tag.name)
