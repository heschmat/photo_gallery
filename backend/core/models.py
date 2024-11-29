"""
Database models.
"""
import os
import uuid

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


def get_path_for_recipe_img(instance, filename):
    """
    Generate a dynamic file path for an uploaded recipe image.

    This function is called by the `upload_to` argument of the `ImageField`
    in the `Recipe` model to determine the storage location of the uploaded
    file. The path includes a unique filename generated using a UUID to ensure
    there are no naming conflicts.

    Args:
        instance: The model instance to which the image is being uploaded.
                  Although not explicitly used in this implementation, it provides
                  context about the model (e.g., access to fields like `instance.id`
                  or `instance.user`) and can be leveraged for custom file paths.
        filename: The original name of the uploaded file, including its extension.

    Returns:
        str: A string representing the file path where the image will be stored.
             The path format is 'uploads/recipe/<unique_uuid>.<file_extension>'.

    Example:
        If a user uploads a file named 'example.jpg', the generated path might be:
        'uploads/recipe/123e4567-e89b-12d3-a456-426614174000.jpg'.

    Notes:
        - The UUID ensures that each uploaded file has a unique name, avoiding
          collisions even if multiple users upload files with the same name.
        - The `instance` argument allows for customization of the path based on
          model attributes if needed, though it is not used in the current implementation.
    """
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'recipe', filename)


# Create your models here. ======================================================== #
# User Model ---------------------------------------------------------------------- #
class UserManager(BaseUserManager):
    """Customized UserManager"""
    def create_user(self, email, password, **params):
        """Create, save & return a new user."""
        if not email:
            raise ValueError('*email* is mandatory for user registration.')
        user = self.model(email=self.normalize_email(email), **params)
        user.set_password(password)  # we save pasword hashes only
        user.save(using=self._db)  # future proof; in case we want to add multiple dbs
        return user

    def create_superuser(self, email, password, **params):
        user = self.create_user(email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User Model."""
    email = models.EmailField(max_length=50, unique=True)
    name = models.CharField(max_length=25)
    is_active = models.BooleanField(default=True)
    # `staff` can login to the admin panel.
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    # Register with email & pass (instead of username/pass)
    USERNAME_FIELD = 'email'


# Recipe Model -------------------------------------------------------------------- #
class Recipe(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    time_minutes = models.PositiveSmallIntegerField()
    cost = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.URLField(max_length=250, blank=True)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(null=True, upload_to=get_path_for_recipe_img)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # set to 'core.User' in config/setttings.py
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title


# Tag Model ----------------------------------------------------------------------- #
class Tag(models.Model):
    """ Tag for filtering recipes. """
    name = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# Ingredient Model ---------------------------------------------------------------- #
class Ingredient(models.Model):
    """Ingredients for recipes."""
    name = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
