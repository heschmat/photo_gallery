"""
Serializers for *recipe* APIs.
"""

from rest_framework import serializers

from core.models import Recipe, Tag


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'cost', 'link']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for *recipe detail* view."""

    class Meta(RecipeSerializer.Meta):
        # `description` will be giving the detail view.
        fields = RecipeSerializer.Meta.fields + ['description']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag."""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']
