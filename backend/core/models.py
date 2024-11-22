"""
Database models.
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


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

# User Model ---------------------------------------------------------------------- #
# User Model ---------------------------------------------------------------------- #
