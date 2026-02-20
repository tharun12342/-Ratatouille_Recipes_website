"""
python manage.py import_data
Imports Global_Food_Recipes_Complete.csv and Complete_Ingredients_Global.csv
"""
import csv
import re
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from recipes.models import Ingredient, Recipe, RecipeIngredient


def safe_float(val, default=0.0):
    try:
        return float(val) if val and val.strip() not in ('', '-', 'None') else default
    except:
        return default


def safe_int(val, default=0):
    try:
        v = re.sub(r'[^\d]', '', str(val))
        return int(v) if v else default
    except:
        return default


def parse_bool(val):
    return str(val).strip().lower() in ('yes', 'true', '1')


class Command(BaseCommand):
    help = 'Import recipes and ingredients from CSV files into the database'

    def add_arguments(self, parser):
        parser.add_argument('--data-dir', default='data', help='Directory containing CSV files')
        parser.add_argument('--skip-recipes', action='store_true')
        parser.add_argument('--skip-ingredients', action='store_true')

    def handle(self, *args, **options):
        data_dir = options['data_dir']
        ing_file = os.path.join(data_dir, 'Complete_Ingredients_Global.csv')
        rec_file = os.path.join(data_dir, 'Global_Food_Recipes_Complete.csv')

        if not options['skip_ingredients']:
            self.import_ingredients(ing_file)
        if not options['skip_recipes']:
            self.import_recipes(rec_file)

        self.stdout.write(self.style.SUCCESS('\n✅ Import complete!'))

    @transaction.atomic
    def import_ingredients(self, filepath):
        self.stdout.write(f'Importing ingredients from {filepath}...')
        Ingredient.objects.all().delete()
        count = 0
        with open(filepath, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                Ingredient.objects.create(
                    ingredient_id=row.get('Ingredient_ID', ''),
                    name=row.get('Ingredient_Name', '').strip(),
                    name_lower=row.get('Ingredient_Lower', '').strip().lower(),
                    category=row.get('Category', '').strip(),
                    subcategory=row.get('Subcategory', '').strip(),
                    is_vegetarian=parse_bool(row.get('Is_Vegetarian', 'Yes')),
                    is_vegan=parse_bool(row.get('Is_Vegan', 'No')),
                    is_gluten_free=parse_bool(row.get('Is_Gluten_Free', 'Yes')),
                    common_usage=row.get('Common_Usage', ''),
                    shelf_life=row.get('Shelf_Life', ''),
                    storage_type=row.get('Storage_Type', ''),
                    typical_unit=row.get('Typical_Unit', ''),
                    hindi_name=row.get('Hindi_Name', ''),
                    regional_names=row.get('Regional_Names', ''),
                    nutrition_highlight=row.get('Nutrition_Highlight', ''),
                    allergen_info=row.get('Allergen_Info', ''),
                    season_available=row.get('Season_Available', ''),
                    price_range=row.get('Price_Range', ''),
                    substitutes=row.get('Substitutes', ''),
                    common_pairings=row.get('Common_Pairings', ''),
                    cooking_method=row.get('Cooking_Method', ''),
                    taste_profile=row.get('Taste_Profile', ''),
                    notes=row.get('Notes', ''),
                    cuisine_origin=row.get('Cuisine_Origin', 'Indian'),
                )
                count += 1
                if count % 200 == 0:
                    self.stdout.write(f'  {count} ingredients...')
        self.stdout.write(self.style.SUCCESS(f'  ✅ {count} ingredients imported'))

    @transaction.atomic
    def import_recipes(self, filepath):
        self.stdout.write(f'Importing recipes from {filepath}...')
        Recipe.objects.all().delete()
        RecipeIngredient.objects.all().delete()

        # Build ingredient lookup: name_lower -> Ingredient
        ing_lookup = {i.name_lower: i for i in Ingredient.objects.all()}
        # Also build partial keys
        ing_keys = list(ing_lookup.keys())

        def find_ingredient(raw_name):
            n = raw_name.lower().strip()
            if n in ing_lookup:
                return ing_lookup[n]
            # Partial match
            for key in ing_keys:
                if key in n or n in key:
                    return ing_lookup[key]
            return None

        count = 0
        ri_bulk = []

        with open(filepath, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                try:
                    recipe = Recipe.objects.create(
                        recipe_id=row.get('Recipe_ID', ''),
                        name=row.get('Recipe_Name', '').strip(),
                        state=row.get('State', ''),
                        region=row.get('Region', ''),
                        country=row.get('Country', 'India'),
                        category=row.get('Category', ''),
                        sub_category=row.get('Sub_Category', ''),
                        ingredients_raw=row.get('Ingredients', ''),
                        prep_time=safe_int(row.get('Preparation_Time_Minutes', 0)),
                        cook_time=safe_int(row.get('Cooking_Time_Minutes', 0)),
                        total_time=safe_int(row.get('Total_Time_Minutes', 0)),
                        servings=safe_int(row.get('Servings', 4), 4),
                        instructions=row.get('Instructions', ''),
                        detailed_instructions=row.get('Detailed_Instructions', ''),
                        calories=safe_float(row.get('Calories_Per_Serving', 0)),
                        protein=safe_float(row.get('Protein_g', 0)),
                        carbohydrates=safe_float(row.get('Carbohydrates_g', 0)),
                        fat=safe_float(row.get('Fat_g', 0)),
                        fiber=safe_float(row.get('Fiber_g', 0)),
                        sodium=safe_float(row.get('Sodium_mg', 0)),
                        iron=safe_float(row.get('Iron_mg', 0)),
                        vitamin_c=safe_float(row.get('Vitamin_C_mg', 0)),
                        difficulty=row.get('Difficulty', ''),
                        is_vegetarian=parse_bool(row.get('Is_Vegetarian', 'No')),
                        is_vegan=parse_bool(row.get('Is_Vegan', 'No')),
                        is_gluten_free=parse_bool(row.get('Is_Gluten_Free', 'No')),
                        image_url=row.get('Image_URL', ''),
                        cuisine_type=row.get('Cuisine_Type', ''),
                        meal_time=row.get('Meal_Time', ''),
                        spice_level=row.get('Spice_Level', ''),
                    )

                    # Link ingredients
                    for part in row.get('Ingredients', '').split(','):
                        raw = re.sub(r'\s*\(.*?\)', '', part).strip()
                        if not raw:
                            continue
                        qty_match = re.search(r'\(([^)]+)\)', part)
                        qty = qty_match.group(1) if qty_match else ''
                        ing = find_ingredient(raw)
                        if ing:
                            ri_bulk.append(RecipeIngredient(recipe=recipe, ingredient=ing, quantity=qty))

                    count += 1
                    if count % 500 == 0:
                        self.stdout.write(f'  {count} recipes...')
                        if ri_bulk:
                            RecipeIngredient.objects.bulk_create(ri_bulk, ignore_conflicts=True)
                            ri_bulk.clear()
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  Skip {row.get("Recipe_Name","?")}: {e}'))

        if ri_bulk:
            RecipeIngredient.objects.bulk_create(ri_bulk, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f'  ✅ {count} recipes imported'))
