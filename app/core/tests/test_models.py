"""
Test database models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from datetime import datetime


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating user with email is success."""

        email = 'test@example.com'
        password = 'testpass123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(email, user.email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_new_recipe(self):
        """Tests creating a new recipe."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            description='Sample recipe description.',
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_new_tag(self):
        """Tests creating a new tag."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_new_ingredient(self):
        """Tests creating a new Ingredient."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(user=user, name='Salt')

        self.assertEqual(str(ingredient), ingredient.name)

    def test_creating_new_home_success(self):
        """Test to create a new home in databse."""
        home = models.Home.objects.create(name='Oakies', parameters='27456')
        self.assertEqual(home.name, str(home))

    def test_create_user_with_home_assigned(self):
        """Test for creating user with home assigned."""
        home = models.Home.objects.create(name='Oakies', parameters='27456')
        user = get_user_model().objects.create_user(
            name='Sarthak',
            email='test@example.com',
            password='testpass123',
            home=home,
        )
        self.assertEqual(user.home, home)

    def test_delete_home_for_existing_user_sucess(self):
        """Deleting home for user assigns null value to home."""
        home = models.Home.objects.create(
            name='Padma Nilaya',
            parameters='27456'
        )
        user = get_user_model().objects.create_user(
            name='Sarthak',
            email='test@example.com',
            password='testpass123',
            home=home,
        )
        home.delete()
        user.refresh_from_db()
        self.assertEqual(user.home, None)

    def test_add_inventory_item(self):
        """Test adding a new inventory ingredient for a home."""
        user = get_user_model().objects.create_user(
            name='Sarthak',
            email='test@example.com',
            password='testpass123',
        )
        home = models.Home.objects.create(
            name='Padma Nilaya',
            parameters='27456'
        )
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Salt',
        )
        inventory = models.Inventory.objects.create(
            home=home,
            ingredient=ingredient,
            amount=500,
        )
        self.assertEqual(inventory.home, home)

    def test_add_home_recipe(self):
        """Test adding home recipe relationship item."""
        user = get_user_model().objects.create_user(
            name='Sarthak',
            email='test@example.com',
            password='testpass123',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            description='Sample recipe description.',
        )
        home = models.Home.objects.create(
            name='Padma Nilaya',
            parameters='27456'
        )
        date = datetime.strptime('02-09-2023', '%d-%m-%Y').date()
        home_recipe = models.FavHomeRecipe.objects.create(
            recipe=recipe,
            home=home,
            last_cooked=date,
            rating=9,
        )
        self.assertEqual(home_recipe.recipe, recipe)

    def test_create_recipe_ingredients(self):
        """Test creating recipe ingredients in the system."""
        user = get_user_model().objects.create_user(
            name='Sarthak',
            email='test@example.com',
            password='testpass123',
        )
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Salt',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            description='Sample recipe description.',
        )
        recipe_ingredient = models.RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount=300,
            mandatory=True,
            amount_unit='g',
        )
        self.assertEqual(recipe_ingredient.recipe, recipe)
