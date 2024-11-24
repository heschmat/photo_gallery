"""
Views for the *recipe* APIs.
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View to manage *recipe* APIs."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Filter the recipes based on who the user is:
    def get_queryset(self):
        """Retrieve recipes for the authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the appropriate serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    # `.perform_create()`
    # This way we can override the behavior of Django when it saves a model in a ViewSet
    def perform_create(self, serializer):
        """Create a new recipe."""
        # Assign the authenticated user to the created recipe.
        serializer.save(user=self.request.user)
