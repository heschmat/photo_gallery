"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


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
