"""
Helper functions for writing testcases.
"""

from core.models import (
    Home,
    Ingredient,
    Inventory,
)
from django.contrib.auth import get_user_model


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
