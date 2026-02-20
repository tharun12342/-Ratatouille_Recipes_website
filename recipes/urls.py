from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('',                         views.home,           name='home'),
    path('match/',                   views.match_recipes,  name='match'),
    path('recipes/',                 views.recipe_list,    name='recipe_list'),
    path('recipes/<int:pk>/',        views.recipe_detail,  name='recipe_detail'),
    path('saved/',                   views.saved_recipes,  name='saved_recipes'),
    path('register/',                views.register,       name='register'),

    # Pantry API
    path('api/pantry/',              views.pantry_list,    name='pantry_list'),
    path('api/pantry/toggle/',       views.pantry_toggle,  name='pantry_toggle'),
    path('api/pantry/clear/',        views.pantry_clear,   name='pantry_clear'),

    # Ingredient API
    path('api/ingredients/<path:category>/', views.ingredients_by_category, name='ingredients_by_cat'),
    path('api/ingredients/search/',  views.ingredient_search, name='ingredient_search'),

    # Match API
    path('api/match/',               views.api_match,      name='api_match'),

    # Save
    path('api/recipes/<int:pk>/save/', views.save_recipe,  name='save_recipe'),
]
