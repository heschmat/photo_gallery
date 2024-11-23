"""
User API Views.
"""

from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,  # our custom defined serializer
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create """
    serializer_class = AuthTokenSerializer
    # This is optional; if not, we won't get browserable api.
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
