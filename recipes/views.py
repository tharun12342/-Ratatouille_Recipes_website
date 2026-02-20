import re
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import Ingredient, Recipe, UserPantry, SavedRecipe


# ─────────────────────────────────────────────────────────────────────────────
# PANTRY HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_pantry(request):
    """Return pantry ingredient IDs for current user/session."""
    if request.user.is_authenticated:
        pantry, _ = UserPantry.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        pantry, _ = UserPantry.objects.get_or_create(session_key=request.session.session_key)
    return pantry


def get_pantry_ingredients(request):
    pantry = get_pantry(request)
    return list(pantry.ingredients.values('id', 'name', 'category', 'name_lower'))


# ─────────────────────────────────────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────────────────────────────────────
@ensure_csrf_cookie
def home(request):
    pantry_items = get_pantry_ingredients(request)
    pantry_ids   = [p['id'] for p in pantry_items]

    # Category icons map — keys must match exact DB category names
    cat_icons = {
        'Vegetables':                  '🥦',
        'Spices & Masalas':            '🌶️',
        'Fruits & Dried Fruits':       '🍊',
        'Grains, Cereals & Flour':     '🌾',
        'Lentils, Legumes & Pulses':   '🫘',
        'Nuts & Seeds':                '🥜',
        'Dairy & Eggs':                '🥛',
        'Meat & Seafood':              '🥩',
        'Herbs':                       '🌿',
        'Oils & Fats':                 '🫙',
        'Sauces, Condiments & Pastes': '🍶',
        'Baking & Dessert Essentials': '🧁',
        'Sweeteners & Sugar':          '🍯',
        'Liquids, Broths & Stocks':    '🍵',
        'Other / Miscellaneous':       '🧺',
        # legacy / fallback names
        'Spices':                      '🌶️',
        'Grains & Cereals':            '🌾',
        'Lentils & Pulses':            '🫘',
        'Dairy Products':              '🥛',
        'Meat & Poultry':              '🍗',
        'Seafood':                     '🦐',
        'Sauces & Condiments':         '🍶',
        'Sweeteners':                  '🍯',
        'Beverages':                   '☕',
        'Pasta & Noodles':             '🍝',
        'Dried Fruits':                '🍇',
        'Flours':                      '🌾',
        'Canned & Preserved':          '🥫',
        'Specialty & International':   '🌍',
    }


    # Cuisine Flags mapping
    cuisine_flags = {
        'Indian': '🇮🇳',
        'Japanese': '🇯🇵',
        'Korean': '🇰🇷',
        'Chinese': '🇨🇳',
        'American': '🇺🇸',
        'German': '🇩🇪',
        'Mexican': '🇲🇽',
        'Thai': '🇹🇭',
        'British': '🇬🇧',
        'Italian': '🇮🇹',
        'French': '🇫🇷',
        'Other': '🌍',
    }

    categories = (
        Ingredient.objects
        .values('category')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    cats_with_icons = [
        {'name': c['category'], 'count': c['count'], 'icon': cat_icons.get(c['category'], '🥘')}
        for c in categories
    ]

    # Top Cuisines for Browse Section
    top_cuisines_qs = (
        Recipe.objects.exclude(cuisine_type='')
        .values('cuisine_type')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    top_cuisines = [
        {
            'name': c['cuisine_type'],
            'count': c['count'],
            'flag': cuisine_flags.get(c['cuisine_type'], '🌍')
        }
        for c in top_cuisines_qs
    ]

    # Quick stats
    stats = {
        'recipes': Recipe.objects.count(),
        'ingredients': Ingredient.objects.count(),
        'cuisines': Recipe.objects.values('cuisine_type').distinct().count(),
        'countries': Recipe.objects.values('country').distinct().count(),
    }

    context = {
        'categories': cats_with_icons,
        'top_cuisines': top_cuisines,
        'pantry_items': pantry_items,
        'pantry_ids': json.dumps(pantry_ids),
        'stats': stats,
    }

    return render(request, 'recipes/home.html', context)


# ─────────────────────────────────────────────────────────────────────────────
# INGREDIENTS API
# ─────────────────────────────────────────────────────────────────────────────
@require_GET
def ingredients_by_category(request, category):
    qs = Ingredient.objects.filter(category=category).order_by('name')
    pantry = get_pantry(request)
    pantry_ids = set(pantry.ingredients.values_list('id', flat=True))
    data = [
        {
            'id': i.id,
            'name': i.name,
            'category': i.category,
            'in_pantry': i.id in pantry_ids,
            'is_veg': i.is_vegetarian,
            'cuisine_origin': i.cuisine_origin,
        }
        for i in qs
    ]
    return JsonResponse({'ingredients': data})


@require_GET
def ingredient_search(request):
    q = request.GET.get('q', '').strip().lower()
    if len(q) < 2:
        return JsonResponse({'ingredients': []})

    # Use 'contains' on the pre-lowercased field. 
    # This avoids 'icontains' issues in some SQLite environments.
    qs = Ingredient.objects.filter(
        Q(name_lower__contains=q) | Q(name__icontains=q)
    ).order_by('name')[:40]
    
    pantry = get_pantry(request)
    pantry_ids = set(pantry.ingredients.values_list('id', flat=True))
    data = [
        {'id': i.id, 'name': i.name, 'category': i.category, 'in_pantry': i.id in pantry_ids}
        for i in qs
    ]
    return JsonResponse({'ingredients': data})


# ─────────────────────────────────────────────────────────────────────────────
# PANTRY API
# ─────────────────────────────────────────────────────────────────────────────
@ensure_csrf_cookie
@require_POST
def pantry_toggle(request):
    data = json.loads(request.body)
    ing_id = data.get('ingredient_id')
    action = data.get('action', 'toggle')
    try:
        ing = Ingredient.objects.get(id=ing_id)
        pantry = get_pantry(request)
        if action == 'add' or (action == 'toggle' and not pantry.ingredients.filter(id=ing_id).exists()):
            pantry.ingredients.add(ing)
            in_pantry = True
        else:
            pantry.ingredients.remove(ing)
            in_pantry = False
        return JsonResponse({'success': True, 'in_pantry': in_pantry, 'name': ing.name})
    except Ingredient.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)


@require_POST
def pantry_clear(request):
    pantry = get_pantry(request)
    pantry.ingredients.clear()
    return JsonResponse({'success': True, 'count': 0})


def pantry_list(request):
    items = get_pantry_ingredients(request)
    return JsonResponse({'ingredients': items, 'count': len(items)})


# ─────────────────────────────────────────────────────────────────────────────
# RECIPE MATCHING
# ─────────────────────────────────────────────────────────────────────────────
def match_recipes(request):
    pantry = get_pantry(request)
    pantry_ings = list(pantry.ingredients.values_list('name_lower', flat=True))

    if not pantry_ings:
        return render(request, 'recipes/match.html', {
            'recipes': [], 'pantry_count': 0, 'pantry_items': []
        })

    pantry_set = set(pantry_ings)
    pantry_items = get_pantry_ingredients(request)

    # Filters
    category   = request.GET.get('category', '')
    cuisine    = request.GET.get('cuisine', '')
    difficulty = request.GET.get('difficulty', '')
    diet       = request.GET.get('diet', '')
    min_match  = int(request.GET.get('min_match', 10))

    qs = Recipe.objects.all()
    if category:   qs = qs.filter(category=category)
    if cuisine:    qs = qs.filter(cuisine_type=cuisine)
    if difficulty: qs = qs.filter(difficulty=difficulty)
    if diet == 'vegetarian': qs = qs.filter(is_vegetarian=True)
    if diet == 'vegan':      qs = qs.filter(is_vegan=True)
    if diet == 'gluten_free': qs = qs.filter(is_gluten_free=True)

    # Score all recipes
    scored = []
    for recipe in qs.only('id','name','category','cuisine_type','difficulty','total_time',
                           'is_vegetarian','spice_level','calories','ingredients_raw','image_url'):
        matched, total, pct = recipe.match_score(pantry_set)
        if pct >= min_match and total > 0:
            scored.append({
                'recipe': recipe,
                'matched': matched,
                'total': total,
                'pct': pct,
                'missing': total - matched,
            })

    scored.sort(key=lambda x: (-x['pct'], -x['matched']))

    # Pagination
    paginator = Paginator(scored, 24)
    page = paginator.get_page(request.GET.get('page', 1))

    categories  = Recipe.objects.values_list('category', flat=True).distinct().order_by('category')
    cuisines    = Recipe.objects.values_list('cuisine_type', flat=True).distinct().order_by('cuisine_type')
    difficulties = ['Easy', 'Medium', 'Hard']

    context = {
        'page': page,
        'pantry_count': len(pantry_items),
        'pantry_items': pantry_items,
        'total_matches': len(scored),
        'categories': categories,
        'cuisines': cuisines,
        'difficulties': difficulties,
        'current_filters': {
            'category': category, 'cuisine': cuisine,
            'difficulty': difficulty, 'diet': diet, 'min_match': min_match,
        },
    }
    return render(request, 'recipes/match.html', context)


# ─────────────────────────────────────────────────────────────────────────────
# RECIPE DETAIL
# ─────────────────────────────────────────────────────────────────────────────
def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    pantry = get_pantry(request)
    pantry_names = set(pantry.ingredients.values_list('name_lower', flat=True))

    # Parse ingredients with match status
    ingredient_list = []
    for part in recipe.ingredients_raw.split(','):
        raw_name = re.sub(r'\s*\(.*?\)', '', part).strip().strip("[]'\" \t")
        qty_match = re.search(r'\(([^)]+)\)', part)
        qty = qty_match.group(1) if qty_match else ''
        if raw_name:
            in_pantry = any(p in raw_name.lower() or raw_name.lower() in p for p in pantry_names)
            ingredient_list.append({'name': raw_name, 'qty': qty, 'in_pantry': in_pantry})

    # Similar recipes
    similar = Recipe.objects.filter(
        Q(cuisine_type=recipe.cuisine_type) | Q(category=recipe.category)
    ).exclude(pk=recipe.pk).order_by('?')[:6]

    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedRecipe.objects.filter(user=request.user, recipe=recipe).exists()

    # Parse instructions
    instructions_list = [s.strip() for s in recipe.instructions.split('.') if s.strip()]

    context = {
        'recipe': recipe,
        'ingredient_list': ingredient_list,
        'instructions_list': instructions_list,
        'similar': similar,
        'is_saved': is_saved,
        'pantry_items': get_pantry_ingredients(request),
    }
    return render(request, 'recipes/detail.html', context)


# ─────────────────────────────────────────────────────────────────────────────
# BROWSE / SEARCH
# ─────────────────────────────────────────────────────────────────────────────
def recipe_list(request):
    q          = request.GET.get('q', '').strip()
    category   = request.GET.get('category', '')
    cuisine    = request.GET.get('cuisine', '')
    difficulty = request.GET.get('difficulty', '')
    diet       = request.GET.get('diet', '')
    sort       = request.GET.get('sort', 'name')

    qs = Recipe.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(ingredients_raw__icontains=q) | Q(cuisine_type__icontains=q))
    if category:   qs = qs.filter(category=category)
    if cuisine:    qs = qs.filter(cuisine_type=cuisine)
    if difficulty: qs = qs.filter(difficulty=difficulty)
    if diet == 'vegetarian': qs = qs.filter(is_vegetarian=True)
    if diet == 'vegan':      qs = qs.filter(is_vegan=True)
    if diet == 'gluten_free': qs = qs.filter(is_gluten_free=True)

    sort_map = {'name': 'name', 'time': 'total_time', 'calories': 'calories', '-calories': '-calories'}
    qs = qs.order_by(sort_map.get(sort, 'name'))

    paginator = Paginator(qs, 24)
    page = paginator.get_page(request.GET.get('page', 1))

    categories  = Recipe.objects.values_list('category', flat=True).distinct().order_by('category')
    cuisines    = Recipe.objects.values_list('cuisine_type', flat=True).distinct().order_by('cuisine_type')

    context = {
        'page': page,
        'total': qs.count(),
        'categories': categories,
        'cuisines': cuisines,
        'difficulties': ['Easy', 'Medium', 'Hard'],
        'current_filters': {'q': q, 'category': category, 'cuisine': cuisine, 'difficulty': difficulty, 'diet': diet, 'sort': sort},
        'pantry_items': get_pantry_ingredients(request),
    }
    return render(request, 'recipes/list.html', context)


# ─────────────────────────────────────────────────────────────────────────────
# MATCH API (AJAX)
# ─────────────────────────────────────────────────────────────────────────────
@require_GET
def api_match(request):
    pantry = get_pantry(request)
    pantry_ings = list(pantry.ingredients.values_list('name_lower', flat=True))
    if not pantry_ings:
        return JsonResponse({'recipes': [], 'count': 0})

    pantry_set = set(pantry_ings)
    min_match = int(request.GET.get('min_match', 10))
    limit = int(request.GET.get('limit', 12))

    scored = []
    for recipe in Recipe.objects.only('id','name','category','cuisine_type','difficulty',
                                      'total_time','is_vegetarian','calories','ingredients_raw'):
        matched, total, pct = recipe.match_score(pantry_set)
        if pct >= min_match and total > 0:
            scored.append({'id': recipe.id, 'name': recipe.name, 'pct': pct,
                           'matched': matched, 'total': total, 'category': recipe.category,
                           'cuisine': recipe.cuisine_type, 'difficulty': recipe.difficulty,
                           'time': recipe.total_time, 'calories': recipe.calories})

    scored.sort(key=lambda x: (-x['pct'], -x['matched']))
    return JsonResponse({'recipes': scored[:limit], 'count': len(scored)})


# ─────────────────────────────────────────────────────────────────────────────
# SAVED RECIPES
# ─────────────────────────────────────────────────────────────────────────────
@login_required
@require_POST
def save_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    obj, created = SavedRecipe.objects.get_or_create(user=request.user, recipe=recipe)
    if not created:
        obj.delete()
        saved = False
    else:
        saved = True
    return JsonResponse({'saved': saved})


@login_required
def saved_recipes(request):
    saved = SavedRecipe.objects.filter(user=request.user).select_related('recipe').order_by('-saved_at')
    return render(request, 'recipes/saved.html', {
        'saved': saved,
        'pantry_items': get_pantry_ingredients(request),
    })


# ─────────────────────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────────────────────
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Migrate session pantry to user
            if request.session.session_key:
                try:
                    session_pantry = UserPantry.objects.get(session_key=request.session.session_key)
                    user_pantry, _ = UserPantry.objects.get_or_create(user=user)
                    for ing in session_pantry.ingredients.all():
                        user_pantry.ingredients.add(ing)
                except UserPantry.DoesNotExist:
                    pass
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
