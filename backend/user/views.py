"""
User API Views.
"""

from rest_framework import generics

from user.serializers import UserSerializer  # our custom defined serializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user."""
    serializer_class = UserSerializer
