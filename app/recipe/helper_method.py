"""
Helper methods for Recipe API test cases.
"""
from django.contrib.auth import get_user_model
from core.models import Tag, Recipe, Ingredient


def create_user(**params):
    defaults = {
        'email': 'test123@example.com',
        'password': 'testpass123'
    }
    defaults.update(params)
    user = get_user_model().objects.create_user(**defaults)
    return user


def create_tag(user, **params):
    defaults = {
        'name': 'Tag 1'
    }
    defaults.update(params)
    tag = Tag.objects.create(user=user, **defaults)

    return tag


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
