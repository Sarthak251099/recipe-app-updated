"""
Helper methods for Recipe API test cases.
"""
from django.contrib.auth import get_user_model
from core.models import (
    Home,
    Tag,
    Recipe,
    Ingredient,
    RecipeIngredient,
    FavHomeRecipe,
    Inventory,
)
from datetime import datetime


def create_user(**params):
    """Create and return a new user."""
    user = get_user_model().objects.create_user(**params)
    return user


def create_home(**params):
    """Create and return a new home."""
    default = {
        'name': 'Oakies',
        'parameters': '673262',
    }
    default.update(params)
    return Home.objects.create(**default)


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


def create_ingredient(user, **params):
    defaults = {
        'name': 'Wheat'
    }
    defaults.update(params)
    ingredient = Ingredient.objects.create(user=user, **defaults)

    return ingredient


def create_recipe_ingredient(recipe, ingredient, **params):
    defaults = {
        'amount': 300,
        'mandatory': True,
        'amount_unit': 'g',
    }
    defaults.update(params)
    recipe_ing = RecipeIngredient.objects.create(
        recipe=recipe,
        ingredient=ingredient,
        **defaults,
    )
    return recipe_ing


def create_tag(user, **params):
    defaults = {
        'name': 'Veg'
    }
    defaults.update(params)
    tag = Tag.objects.create(user=user, **defaults)

    return tag


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


def add_to_inventory(home, ingredient, **params):
    """Add ingredient item to inventory of home."""
    return Inventory.objects.create(
        home=home,
        ingredient=ingredient,
        **params,
        )
