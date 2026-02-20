from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ingredient_id', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(db_index=True, max_length=200)),
                ('name_lower', models.CharField(db_index=True, max_length=200)),
                ('category', models.CharField(db_index=True, max_length=100)),
                ('subcategory', models.CharField(blank=True, max_length=100)),
                ('is_vegetarian', models.BooleanField(default=True)),
                ('is_vegan', models.BooleanField(default=False)),
                ('is_gluten_free', models.BooleanField(default=True)),
                ('common_usage', models.TextField(blank=True)),
                ('shelf_life', models.CharField(blank=True, max_length=100)),
                ('storage_type', models.CharField(blank=True, max_length=100)),
                ('typical_unit', models.CharField(blank=True, max_length=50)),
                ('hindi_name', models.CharField(blank=True, max_length=200)),
                ('regional_names', models.TextField(blank=True)),
                ('nutrition_highlight', models.TextField(blank=True)),
                ('allergen_info', models.CharField(blank=True, max_length=200)),
                ('season_available', models.CharField(blank=True, max_length=100)),
                ('price_range', models.CharField(blank=True, max_length=50)),
                ('substitutes', models.TextField(blank=True)),
                ('common_pairings', models.TextField(blank=True)),
                ('cooking_method', models.TextField(blank=True)),
                ('taste_profile', models.TextField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('cuisine_origin', models.CharField(blank=True, default='Indian', max_length=100)),
            ],
            options={'ordering': ['category', 'name']},
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe_id', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(db_index=True, max_length=300)),
                ('state', models.CharField(blank=True, max_length=100)),
                ('region', models.CharField(blank=True, db_index=True, max_length=100)),
                ('country', models.CharField(blank=True, db_index=True, max_length=100)),
                ('category', models.CharField(db_index=True, max_length=100)),
                ('sub_category', models.CharField(blank=True, max_length=100)),
                ('ingredients_raw', models.TextField()),
                ('prep_time', models.IntegerField(default=0)),
                ('cook_time', models.IntegerField(default=0)),
                ('total_time', models.IntegerField(default=0, db_index=True)),
                ('servings', models.IntegerField(default=4)),
                ('instructions', models.TextField()),
                ('detailed_instructions', models.TextField(blank=True)),
                ('calories', models.FloatField(default=0)),
                ('protein', models.FloatField(default=0)),
                ('carbohydrates', models.FloatField(default=0)),
                ('fat', models.FloatField(default=0)),
                ('fiber', models.FloatField(default=0)),
                ('sodium', models.FloatField(default=0)),
                ('iron', models.FloatField(default=0)),
                ('vitamin_c', models.FloatField(default=0)),
                ('difficulty', models.CharField(blank=True, db_index=True, max_length=20)),
                ('is_vegetarian', models.BooleanField(db_index=True, default=False)),
                ('is_vegan', models.BooleanField(default=False)),
                ('is_gluten_free', models.BooleanField(default=False)),
                ('image_url', models.URLField(blank=True)),
                ('cuisine_type', models.CharField(blank=True, db_index=True, max_length=100)),
                ('meal_time', models.CharField(blank=True, max_length=100)),
                ('spice_level', models.CharField(blank=True, max_length=50)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.CharField(blank=True, max_length=50)),
                ('unit', models.CharField(blank=True, max_length=50)),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.ingredient')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe')),
            ],
            options={'unique_together': {('recipe', 'ingredient')}},
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(blank=True, through='recipes.RecipeIngredient', to='recipes.ingredient'),
        ),
        migrations.CreateModel(
            name='UserPantry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, db_index=True, max_length=40)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ingredients', models.ManyToManyField(blank=True, to='recipes.ingredient')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='SavedRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('saved_at', models.DateTimeField(auto_now_add=True)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={'unique_together': {('user', 'recipe')}},
        ),
        migrations.AddIndex(
            model_name='ingredient',
            index=models.Index(fields=['category'], name='recipes_ing_categor_idx'),
        ),
        migrations.AddIndex(
            model_name='ingredient',
            index=models.Index(fields=['name_lower'], name='recipes_ing_name_lo_idx'),
        ),
        migrations.AddIndex(
            model_name='recipe',
            index=models.Index(fields=['category'], name='recipes_rec_categor_idx'),
        ),
        migrations.AddIndex(
            model_name='recipe',
            index=models.Index(fields=['cuisine_type'], name='recipes_rec_cuisine_idx'),
        ),
    ]
