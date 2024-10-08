"""
Database models.
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class Home(models.Model):
    """Home object."""
    name = models.CharField(max_length=255, default='Home')
    parameters = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    home = models.ForeignKey(
        Home,
        null=True,
        on_delete=models.SET_NULL,
        related_name='users'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Recipe(models.Model):
    """Recipe object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    link = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tag for filtering recipes."""
    name = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient for recipes."""
    name = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Inventory(models.Model):
    """Inventory for home."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField()
    amount_unit = models.CharField(max_length=100, default='g')

    def __str__(self):
        return (
            f'Ingredient: {self.ingredient}, '
            f'Home: {self.home}, '
            f'Amount: {self.amount}'
        )


class FavHomeRecipe(models.Model):
    """Home recipe favourites."""
    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name='favourites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    last_cooked = models.DateField(null=True, blank=True)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ('home', 'recipe')


class RecipeIngredient(models.Model):
    """Recipe ingredient model."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField()
    mandatory = models.BooleanField(default=False)
    amount_unit = models.CharField(max_length=100)

    class Meta:
        unique_together = ('ingredient', 'recipe')
