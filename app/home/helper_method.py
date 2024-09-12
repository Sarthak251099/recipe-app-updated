"""
Helper functions for writing testcases.
"""

from core.models import (
    Home,
    Ingredient,
    Inventory,
    FavHomeRecipe,
    Recipe,
)
from django.contrib.auth import get_user_model
from datetime import datetime


def create_home(**params):
    """Create and return a new home."""
    default = {
        'name': 'Oakies',
        'parameters': '673262',
    }
    default.update(params)
    return Home.objects.create(**default)


def create_ingredient(user, **params):
    """Create and return an ingredient."""

    ingredient = Ingredient.objects.create(user=user, **params)

    return ingredient


def add_to_inventory(home, ingredient, amount=500):
    """Add ingredient item to inventory of home."""
    return Inventory.objects.create(
        home=home,
        ingredient=ingredient,
        amount=amount,
        )


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


def create_recipe(user, **params):
    """Create and return a new recipe."""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'description': 'Sample Description',
        'link': 'http://example.com/recipe.pdf'
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_fav_recipe(home, recipe, **params):
    """Create and return a new fav recipe object."""
    date = datetime.strptime('02-09-2023', '%d-%m-%Y').date()
    defaults = {
        'last_cooked': date,
        'rating': 5,
    }
    defaults.update(params)

    fav_home_recipe = FavHomeRecipe.objects.create(
        home=home,
        recipe=recipe,
        **params,
    )
    return fav_home_recipe
