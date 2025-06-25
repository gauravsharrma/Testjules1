from flask import Flask, render_template, request, url_for

app = Flask(__name__)

# --- App Data ---
APPS_DATA = [
    {
        "slug": "emi-calculator",
        "name": "EMI Calculator",
        "icon": "placeholder_icon.png",
        "description": "Calculate Equated Monthly Installments for loans.",
        "category": "Finance",
        "module": "emi_calculator" # For importing app-specific routes/logic
    },
    {
        "slug": "bmi-calculator",
        "name": "BMI Calculator",
        "icon": "placeholder_icon.png",
        "description": "Calculate Body Mass Index.",
        "category": "Health",
        "module": "bmi_calculator"
    }
]

# Dynamically get unique categories from APPS_DATA
CATEGORIES = sorted(list(set(app['category'] for app in APPS_DATA)))

@app.route('/')
def index():
    query = request.args.get('search', '').lower()
    category_filter = request.args.get('category', '').lower()

    filtered_apps = APPS_DATA
    if query:
        filtered_apps = [app for app in filtered_apps if query in app['name'].lower()]
    if category_filter:
        filtered_apps = [app for app in filtered_apps if category_filter == app['category'].lower()]

    return render_template('index.html', apps=filtered_apps, categories=CATEGORIES, search_query=query, current_category=category_filter)

# --- App specific routes will be imported and registered here ---
from apps.emi_calculator import emi_bp
app.register_blueprint(emi_bp)

from apps.bmi_calculator import bmi_bp
app.register_blueprint(bmi_bp)

# General handler for app slugs, typically for apps not yet having dedicated blueprints
# or for a generic way to view app info if desired.
# For apps with blueprints, direct linking from index.html (or elsewhere) to the blueprint's routes is preferred.
@app.route('/apps/<app_slug>')
def app_page(app_slug):
    app_info = next((app for app in APPS_DATA if app['slug'] == app_slug), None)
    if app_info:
        # This page will now primarily serve as a placeholder if an app is not directly linked
        # to its blueprint route from the main page, or if a blueprint isn't implemented.
        return render_template('app_placeholder.html', app=app_info)
    return "App not found", 404

if __name__ == '__main__':
    app.run(debug=True)
