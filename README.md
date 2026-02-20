# 🍴 RecipeMatch

**Cook what you actually have.** An ingredient-first recipe discovery app inspired by SuperCook — built with Django, MySQL, and vanilla JavaScript.

![RecipeMatch](https://via.placeholder.com/1200x600/0E0F0F/E8C547?text=RecipeMatch+%E2%80%94+Cook+What+You+Have)

---

## ✨ Features

- 🧺 **Smart Pantry** — Add ingredients by browsing 20 categories or quick-searching. Pantry persists without login via sessions.
- 🎯 **Ingredient Matching** — Every recipe is scored by how many of your pantry ingredients it uses. Sort by best match.
- 🌍 **10,064 Global Recipes** — 10,000 Indian recipes + 64 world-famous dishes from 20 countries (Italian, French, Japanese, Mexican, Chinese, Korean, Thai, Indonesian, Moroccan, Ethiopian, Nigerian, Spanish, Greek, American, British, German, Peruvian and more).
- 🔍 **Advanced Filters** — Filter by category, cuisine, difficulty, diet (vegetarian/vegan/gluten-free), and minimum match %.
- 📖 **Detailed Instructions** — Every recipe includes a full chef's guide with equipment, step-by-step method, tips, nutrition, and storage notes.
- ❤️ **Save Recipes** — Logged-in users can save favourites.
- 📱 **Responsive** — Works great on mobile.

---

## 🛠 Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | Python 3.11 + Django 4.2          |
| Database   | MySQL 8 (SQLite for local dev)    |
| Frontend   | HTML5 + CSS3 + Vanilla JavaScript |
| Fonts      | Fraunces + DM Sans (Google Fonts) |
| Production | Gunicorn + WhiteNoise             |

---

## 🚀 Quick Start (Local Dev with SQLite)

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/recipematch.git
cd recipematch
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment
```bash
cp .env.example .env
# Edit .env — for local dev the defaults work fine
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Add the data files
Place these two CSV files into the `data/` directory:
- `data/Global_Food_Recipes_Complete.csv`
- `data/Complete_Ingredients_Global.csv`

### 7. Import data (takes ~2-3 minutes)
```bash
python manage.py import_data
```

### 8. Create admin user
```bash
python manage.py createsuperuser
```

### 9. Run the server
```bash
python manage.py runserver
```

Open http://127.0.0.1:8000 🎉

---

## 🗄 MySQL Setup (Production / Full Setup)

### Install MySQL
```bash
# Ubuntu/Debian
sudo apt install mysql-server libmysqlclient-dev

# macOS
brew install mysql pkg-config
```

### Create database
```sql
mysql -u root -p
CREATE DATABASE recipematch CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'recipematch'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON recipematch.* TO 'recipematch'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Update .env
```env
DB_ENGINE=mysql
DB_NAME=recipematch
DB_USER=recipematch
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

### Run migrations and import
```bash
python manage.py migrate
python manage.py import_data
```

---

## 📁 Project Structure

```
recipematch/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   ├── Global_Food_Recipes_Complete.csv      # 10,064 recipes
│   └── Complete_Ingredients_Global.csv        # 2,036 ingredients
│
├── recipematch/                   # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── recipes/                       # Main app
│   ├── models.py                  # Ingredient, Recipe, UserPantry, SavedRecipe
│   ├── views.py                   # All view logic + REST API endpoints
│   ├── urls.py                    # URL routing
│   ├── admin.py
│   ├── migrations/
│   └── management/
│       └── commands/
│           └── import_data.py     # CSV import command
│
├── templates/
│   ├── base.html                  # Nav, pantry drawer, toast system
│   └── recipes/
│       ├── home.html              # Ingredient selector + hero
│       ├── match.html             # Matching results + filters
│       ├── list.html              # Browse all recipes
│       ├── detail.html            # Recipe detail page
│       └── saved.html             # Saved recipes
│
└── static/
    ├── css/
    └── js/
```

---

## 🔌 API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/pantry/` | Get current pantry items |
| POST | `/api/pantry/toggle/` | Add/remove ingredient from pantry |
| POST | `/api/pantry/clear/` | Clear entire pantry |
| GET | `/api/ingredients/<category>/` | Get ingredients by category |
| GET | `/api/ingredients/search/?q=` | Search ingredients |
| GET | `/api/match/?min_match=50` | Get matching recipes (JSON) |
| POST | `/api/recipes/<pk>/save/` | Toggle save a recipe |

---

## 🚢 GitHub Setup

### Initialize and push
```bash
cd recipematch
git init
git add .
git commit -m "Initial commit — RecipeMatch v1.0"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/recipematch.git
git branch -M main
git push -u origin main
```

### ⚠️ Important: The large CSV files
The data CSVs are ~48MB total. Either:

**Option A — Include in repo (simple)**
```bash
# Remove data/ from .gitignore, then commit
git add data/
git commit -m "Add recipe and ingredient data"
```

**Option B — Git LFS (recommended for large files)**
```bash
git lfs install
git lfs track "data/*.csv"
git add .gitattributes
git add data/
git commit -m "Add data with LFS"
```

**Option C — Separate releases**
Upload the CSVs as a GitHub Release asset and document the download step in README.

---

## 🌐 Deploying to Production

### Option A: Railway (Easiest)
1. Push to GitHub
2. Create new project on [railway.app](https://railway.app)
3. Add MySQL plugin
4. Set environment variables from `.env.example`
5. Set start command: `gunicorn recipematch.wsgi`
6. Run `python manage.py migrate` and `python manage.py import_data`

### Option B: Render
1. New Web Service → Connect GitHub repo
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn recipematch.wsgi`
4. Add MySQL database and set env vars

### Option C: VPS (Ubuntu)
```bash
# Install nginx, gunicorn, mysql
sudo apt install nginx mysql-server python3-venv

# Clone and set up
git clone https://github.com/YOUR/recipematch.git /var/www/recipematch
cd /var/www/recipematch
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in production values

# Collect static files
python manage.py collectstatic

# Gunicorn service + Nginx config
# (see docs/nginx.conf and docs/gunicorn.service in the repo)
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | — | Django secret key (**change in prod!**) |
| `DEBUG` | `True` | Set to `False` in production |
| `ALLOWED_HOSTS` | `*` | Comma-separated allowed hosts |
| `DB_ENGINE` | `sqlite` | `sqlite` or `mysql` |
| `DB_NAME` | `recipematch` | Database name |
| `DB_USER` | `root` | Database user |
| `DB_PASSWORD` | — | Database password |
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `3306` | MySQL port |

---

## 🗂 Data Sources

- **Indian Recipes**: 10,000 authentic recipes across 6 Indian regions, 28+ states
- **World Recipes**: 64 hand-crafted recipes from 16 world cuisines
- **Ingredients**: 2,036 ingredients with 24 attributes each (Hindi names, nutrition, substitutes, etc.)

---

## 📄 License

MIT License — free to use, modify, and deploy.

---

## 🤝 Contributing

Pull requests welcome! Areas to improve:
- Add more world recipes
- Better image handling (Unsplash API integration)
- User recipe ratings/reviews
- Meal planner / shopping list feature
- Recipe scaling calculator
