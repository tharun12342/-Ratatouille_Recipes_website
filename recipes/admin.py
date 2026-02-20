from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient, UserPantry, SavedRecipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'cuisine_origin', 'is_vegetarian']
    list_filter  = ['category', 'cuisine_origin', 'is_vegetarian']
    search_fields = ['name', 'name_lower']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'cuisine_type', 'category', 'difficulty', 'total_time']
    list_filter  = ['cuisine_type', 'category', 'difficulty', 'is_vegetarian']
    search_fields = ['name', 'cuisine_type']


@admin.register(UserPantry)
class PantryAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'updated_at']

admin.site.register(RecipeIngredient)
admin.site.register(SavedRecipe)
