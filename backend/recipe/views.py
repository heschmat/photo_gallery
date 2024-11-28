"""
Views for the *recipe* APIs.
"""

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag
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


# N.B. make suer `GenericViewSet` comes aftre `**ModelMixin`.
# `viewsets.GenericViewSet` class automatically maps HTTP methods
# to the appropriate mixin methods, based on the Django REST Framework's conventions.
class TagViewSet(
    mixins.DestroyModelMixin,  # DELETE /api/tags/<id>/
    mixins.UpdateModelMixin,  # PATCH|PUT /api/tags/<id>/
    mixins.ListModelMixin,  # GET /api/tags/
    viewsets.GenericViewSet
):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]  # who is the user (authentication)
    permission_classes = [IsAuthenticated]  # is the user authorized?

    def get_queryset(self):
        # N.B. No need to check if user is authenticated, due to `permission_classes` set.
        # if not self.request.user.is_authenticated:
        #     # Return an empty queryset for unauthenticated users
        #     return Tag.objects.none()
        return self.queryset.filter(user=self.request.user).order_by('-name')


"""
authentication_classes = [TokenAuthentication]

The request must include a valid token.
If the token is valid, request.user is set to the authenticated user.
If the token is invalid, request.user is set to `AnonymousUser`.

# ----------------------------------------------------------
permission_classes = [IsAuthenticated]

If the user is authenticated (IsAuthenticated), they can proceed.
If the user is unauthenticated, the API returns an HTTP 401 Unauthorized response,
and the view’s logic (like get_queryset) is never executed.

# -----------------------------------------------------------

The DestroyModelMixin provides a default implementation of the destroy method.
Here's how it works:
```py
def destroy(self, request, *args, **kwargs):
    instance = self.get_object()
    self.perform_destroy(instance)
    return Response(status=status.HTTP_204_NO_CONTENT)
```
"""
