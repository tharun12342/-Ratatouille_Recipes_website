from django.db import models
from django.contrib.auth.models import User


class Ingredient(models.Model):
    ingredient_id   = models.CharField(max_length=20, unique=True)
    name            = models.CharField(max_length=200, db_index=True)
    name_lower      = models.CharField(max_length=200, db_index=True)
    category        = models.CharField(max_length=100, db_index=True)
    subcategory     = models.CharField(max_length=100, blank=True)
    is_vegetarian   = models.BooleanField(default=True)
    is_vegan        = models.BooleanField(default=False)
    is_gluten_free  = models.BooleanField(default=True)
    common_usage    = models.TextField(blank=True)
    shelf_life      = models.CharField(max_length=100, blank=True)
    storage_type    = models.CharField(max_length=100, blank=True)
    typical_unit    = models.CharField(max_length=50, blank=True)
    hindi_name      = models.CharField(max_length=200, blank=True)
    regional_names  = models.TextField(blank=True)
    nutrition_highlight = models.TextField(blank=True)
    allergen_info   = models.CharField(max_length=200, blank=True)
    season_available = models.CharField(max_length=100, blank=True)
    price_range     = models.CharField(max_length=50, blank=True)
    substitutes     = models.TextField(blank=True)
    common_pairings = models.TextField(blank=True)
    cooking_method  = models.TextField(blank=True)
    taste_profile   = models.TextField(blank=True)
    notes           = models.TextField(blank=True)
    cuisine_origin  = models.CharField(max_length=100, blank=True, default='Indian')

    class Meta:
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['name_lower']),
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    recipe_id       = models.CharField(max_length=20, unique=True)
    name            = models.CharField(max_length=300, db_index=True)
    state           = models.CharField(max_length=100, blank=True)
    region          = models.CharField(max_length=100, blank=True, db_index=True)
    country         = models.CharField(max_length=100, blank=True, db_index=True)
    category        = models.CharField(max_length=100, db_index=True)
    sub_category    = models.CharField(max_length=100, blank=True)
    ingredients_raw = models.TextField()
    prep_time       = models.IntegerField(default=0)
    cook_time       = models.IntegerField(default=0)
    total_time      = models.IntegerField(default=0, db_index=True)
    servings        = models.IntegerField(default=4)
    instructions    = models.TextField()
    detailed_instructions = models.TextField(blank=True)
    calories        = models.FloatField(default=0)
    protein         = models.FloatField(default=0)
    carbohydrates   = models.FloatField(default=0)
    fat             = models.FloatField(default=0)
    fiber           = models.FloatField(default=0)
    sodium          = models.FloatField(default=0)
    iron            = models.FloatField(default=0)
    vitamin_c       = models.FloatField(default=0)
    difficulty      = models.CharField(max_length=20, blank=True, db_index=True)
    is_vegetarian   = models.BooleanField(default=False, db_index=True)
    is_vegan        = models.BooleanField(default=False)
    is_gluten_free  = models.BooleanField(default=False)
    image_url       = models.URLField(blank=True)
    cuisine_type    = models.CharField(max_length=100, blank=True, db_index=True)
    meal_time       = models.CharField(max_length=100, blank=True)
    spice_level     = models.CharField(max_length=50, blank=True)
    # M2M to ingredients
    ingredients     = models.ManyToManyField(Ingredient, through='RecipeIngredient', blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['cuisine_type']),
            models.Index(fields=['difficulty']),
            models.Index(fields=['is_vegetarian']),
        ]

    def __str__(self):
        return self.name

    @property
    def ingredient_names(self):
        import re
        names = []
        for part in self.ingredients_raw.split(','):
            # Strip surrounding brackets and single/double quotes from the raw data
            # (ingredients_raw may be stored as a Python list literal string)
            clean = re.sub(r'\s*\(.*?\)', '', part).strip()
            clean = clean.strip("[]'\"\\ \t")
            if clean:
                names.append(clean)
        return names

    def match_score(self, pantry_set):
        """
        Score = how many of YOUR pantry items appear in this recipe.
        Returns (matched_pantry_count, total_pantry_count, match_pct)
        So if all 5 of your pantry items appear in a recipe, score = 100%,
        regardless of how many total ingredients the recipe has.
        """
        if not pantry_set:
            return 0, 0, 0

        # Clean recipe ingredient names (strip quotes/brackets from raw data)
        names_lower = [n.lower().strip("[]'\" \t") for n in self.ingredient_names]
        pantry_lower = [p.lower().strip() for p in pantry_set]

        # Count how many pantry items appear in the recipe ingredient list
        matched = sum(
            1 for p in pantry_lower
            if any(p in ing or ing in p for ing in names_lower)
        )
        total = len(pantry_lower)
        return matched, total, round(matched / total * 100)

    @property
    def visual_dna(self):
        """
        Generates a deterministic visual identity for the recipe based on its name.
        Returns a dict with hue, sat, lit, and animation timing.
        """
        import zlib
        # Use adler32 for a fast, stable hash across restarts
        h = zlib.adler32(self.name.encode('utf-8')) & 0xffffffff
        
        return {
            'hue': h % 360,                # 0-360 degrees
            'sat': 80 + (h % 20),          # 80-100% saturation
            'lit': 45 + (h % 15),          # 45-60% lightness
            'delay': (h % 50) / -10.0,     # 0.0s to -5.0s delay (start mid-animation)
            'duration': 3.0 + ((h % 30) / 10.0) # 3.0s to 6.0s float duration
        }



class RecipeIngredient(models.Model):
    recipe      = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient  = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity    = models.CharField(max_length=50, blank=True)
    unit        = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ('recipe', 'ingredient')


class UserPantry(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    ingredients = models.ManyToManyField(Ingredient, blank=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pantry({'user:'+self.user.username if self.user else 'session:'+self.session_key})"


class SavedRecipe(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe      = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    saved_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')
