"""
Test suits for the *user* API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


# `user:create` should match the info in `user/urls.py`:
# app_name = user;
# `name` passed to `path` is `create`
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
PROFILE_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """
    Test the public functionalities of the *user* api.
    i.e., no authentication required.
    """

    def setUp(self):
        self.client = APIClient()
        self.default_payload = {
            'email': 'user1@example.com',
            'password': 'Whatever!',
            'name': 'Skye Q',
        }

    def _get_payload(self, **overrides):
        """Helper method to generate a payload with optional overrides."""
        payload = self.default_payload.copy()
        payload.update(overrides)
        return payload

    def test_create_user_ok(self):
        payload = self._get_payload()
        # Make a POST request to the API:
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Retrieve the created user with the given email address from the DB.
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))

        # Security check: password should not be returned.
        self.assertNotIn('password', res.data)

    def test_create_user_exists_err(self):
        """Tests an already registered user cannot be re-created."""
        payload = self._get_payload()
        _ = create_user(**payload)  # create a user with the given info

        # Try creating a user with the same email above:
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_short_password_err(self):
        """Test password is """
        payload = self._get_payload(password='123')
        res = self.client.post(CREATE_USER_URL, payload)
        # Passwords shorter than 8 chars should fail (as defined in `UserSerializer`).
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Make sure the above user is not available in the DB (i.e., not created)
        user = get_user_model().objects.filter(email=payload['email'])
        self.assertFalse(user.exists())

    def test_create_token_for_new_user(self):
        """Test generates token for valid credentials."""
        user_info = self._get_payload()
        _ = create_user(**user_info)

        # Send a POST request to the token URL:
        payload = {k: v for k, v in user_info.items() if k != 'name'}
        res = self.client.post(TOKEN_URL, payload)

        # Make sure the request is success & `token` is returned.
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_bad_credentials_fail(self):
        """Test invalid credentials fail."""
        payload = self._get_payload()
        # Create a new user with the above credentials.
        _ = create_user(**payload)

        # Modify the payload to have wrong credentials for the user.
        # payload.update({'password': 'wrong_password'})
        payload['password'] = 'wrong_password'
        # Make a POST request to the `token` url with wrong credentials.
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_profile_access_unauth_user_fail(self):
        """Test only authenticated users have profile (access)"""
        # Make an unauthenticated GET request to profile page.
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserAPITests(TestCase):
    """Test suits for authenticated users."""
    def setUp(self):
        # Create a new user & authenticate:
        payload = {'email': 'user1@example.com', 'password': 'Whatever!', 'name': 'JJ'}
        self.user = create_user(**payload)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_ok(self):
        """Test authenticated user can access their profile."""
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'email': self.user.email, 'name': self.user.name})

    def test_post_method_profile_page_not_allowed(self):
        """Test /api/user/me cannot be used for user creation.
        /api/user/create is the proper endpoint for this purpose.
        """
        res = self.client.post(PROFILE_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_profile_ok(self):
        """Test authenticated user can update their profile."""
        payload_updated = {'name': 'Some other name', 'password': 'More s3cure pa$$'}
        res = self.client.patch(PROFILE_URL, payload_updated)

        # Fetch the recent data from the db.
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload_updated['name'])
        self.assertTrue(self.user.check_password(payload_updated['password']))
