"""
User API Views.
"""

from rest_framework import generics, authentication, permissions
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
    # visiting /api/user/token/ in the browser we get => 'Method "GET" not allowed.'
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user: /api/me/"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]  # authentication
    permission_classes = [permissions.IsAuthenticated]  # authorization

    def get_object(self):
        """Retrieve & return the authenticated user."""
        return self.request.user
