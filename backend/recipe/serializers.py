"""
Serializers for *recipe* APIs.
"""

from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag."""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient."""
    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'cost', 'link', 'tags']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags."""
        # Get the user from the serializer object:
        user_authenticated = self.context['request'].user
        # Now, create/add the tags:
        for tag in tags:
            # `.get_or_create()` won't create duplicate tags as the name suggests.
            tag_obj, created = Tag.objects.get_or_create(user=user_authenticated, **tag)
            recipe.tags.add(tag_obj)

    # Add "write" functionality to our nested serializer.
    # By default, they'll be read-only.
    def create(self, validated_data):
        """Create a recipe."""
        # Remove the `tag` key from the recipe payload.
        recipe_tags = validated_data.pop('tags', [])
        # `create` the recipe with the payload (no tags)
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(recipe_tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Update the recipe."""
        recipe_tags = validated_data.pop('tags', None)
        if recipe_tags is not None:
            instance.tags.clear()  # Clear existing tags
            self._get_or_create_tags(recipe_tags, instance)

        for attr, val in validated_data.items():
            setattr(instance, attr, val)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for *recipe detail* view."""

    class Meta(RecipeSerializer.Meta):
        # `description` will be giving the detail view.
        fields = RecipeSerializer.Meta.fields + ['description']
