from django.test import TestCase, Client
from django.urls import reverse
from .models import Ingredient, Recipe


class IngredientModelTest(TestCase):
    def setUp(self):
        self.ing = Ingredient.objects.create(
            ingredient_id='TEST001',
            name='Tomato',
            name_lower='tomato',
            category='Vegetables',
        )

    def test_ingredient_str(self):
        self.assertEqual(str(self.ing), 'Tomato')

    def test_ingredient_category(self):
        self.assertEqual(self.ing.category, 'Vegetables')


class RecipeModelTest(TestCase):
    def setUp(self):
        self.recipe = Recipe.objects.create(
            recipe_id='TEST001',
            name='Test Curry',
            ingredients_raw='Tomato (2), Onion (1), Oil',
            category='Main Course',
            cuisine_type='Indian',
            difficulty='Easy',
        )

    def test_recipe_str(self):
        self.assertEqual(str(self.recipe), 'Test Curry')

    def test_ingredient_names(self):
        names = self.recipe.ingredient_names
        self.assertIn('Tomato', names)
        self.assertIn('Onion', names)

    def test_match_score_empty_pantry(self):
        m, t, pct = self.recipe.match_score(set())
        self.assertEqual(pct, 0)

    def test_match_score_full_match(self):
        m, t, pct = self.recipe.match_score({'tomato', 'onion', 'oil'})
        self.assertEqual(pct, 100)


class ViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_loads(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)

    def test_recipe_list_loads(self):
        r = self.client.get('/recipes/')
        self.assertEqual(r.status_code, 200)

    def test_match_page_loads(self):
        r = self.client.get('/match/')
        self.assertEqual(r.status_code, 200)

    def test_pantry_api(self):
        r = self.client.get('/api/pantry/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('ingredients', data)

    def test_ingredient_search_api(self):
        Ingredient.objects.create(ingredient_id='T1', name='Turmeric', name_lower='turmeric', category='Spices')
        r = self.client.get('/api/ingredients/search/?q=turm')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(len(data['ingredients']), 1)
