"""
Serializers for the User API View.
"""

from django.contrib.auth import get_user_model, authenticate

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        # extra_fields = {'password': {'write_only': True, 'min_length': 8}}
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    # Overwrite the `create` method to use the `validate_data` by the serializer
    # for example, the password is 8 char long at least.
    # and not just the raw json passed.
    def create(self, validated_data):
        """Create & return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        # If user didn't update the password, `validated_data` has no such key.
        # In this case, we return None (i.e., nothing further to handle in that regard.)
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            # We ALWAYS keep the hash of passowrds only.
            # That's why we, above, popped the `password` from `validated_data`.
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False
    )

    def validate(self, attrs):
        """"""
        # Check if the credentials match, return the user.
        user = authenticate(
            request=self.context.get('request'),
            # N.B. we modified the app so that the login happens by `email`, not `username`
            username=attrs.get('email'),
            password=attrs.get('password')
        )
        if not user:
            msg = 'Credentials do NOT match!'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
