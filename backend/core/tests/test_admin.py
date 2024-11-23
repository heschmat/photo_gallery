"""
Test for the Django admin modifications.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Test for Django Admin."""

    # `setUp` runs before every test. it's from `unittest` library.
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            email='admin@example.com', password='JeSuiAdmin!'
        )

        # Create test user:
        self.user = get_user_model().objects.create_user(
            email='user1@example.com', password='Whatever!', name='Lily'
        )

        # Create client
        self.client = Client()
        self.client.force_login(self.admin)

    def test_user_listed_on_admin_page(self):
        # https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#reversing-admin-urls
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)  # makes a HTTP GET request to the URL

        # Check `name` & `email` are present in the listing:
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_change_user_page(self):
        """
        e.g., `/admin/core/user/1/change/`
        """
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_add_user_page(self):
        """
        e.g., /admin/core/user/add/
        """
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
