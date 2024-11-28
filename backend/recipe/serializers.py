"""
Serializers for *recipe* APIs.
"""

from rest_framework import serializers

from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag."""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'cost', 'link', 'tags']
        read_only_fields = ['id']

    # Add "write" functionality to our nested serializer.
    # By default, they'll be read-only.
    def create(self, validated_data):
        """Create a recipe."""
        # Remove the `tag` key from the recipe payload.
        recipe_tags = validated_data.pop('tags', [])
        # `create` the recipe with the payload (no tags)
        recipe = Recipe.objects.create(**validated_data)
        # Get the user from the serializer object:
        user_authenticated = self.context['request'].user
        # Now, create/add the tags:
        for tag in recipe_tags:
            # `.get_or_create()` won't create duplicate tags as the name suggests.
            tag_obj, created = Tag.objects.get_or_create(user=user_authenticated, **tag)
            recipe.tags.add(tag_obj)

        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for *recipe detail* view."""

    class Meta(RecipeSerializer.Meta):
        # `description` will be giving the detail view.
        fields = RecipeSerializer.Meta.fields + ['description']
