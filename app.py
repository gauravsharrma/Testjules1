from flask import Flask, render_template, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user # We'll define User model later
import os

# Import configuration
from config import load_app_config

app = Flask(__name__)
app.config.from_object(load_app_config())

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
# login_manager.login_view = 'auth_bp.login' # Will be updated to auth_bp.login
login_manager.login_message_category = "info"


# Import models here to ensure they are registered with SQLAlchemy
# and for Flask-Migrate to detect them.
# Also for login_manager.user_loader to find User model.
from models import User, OAuth # Import the new OAuth model

# Flask-Dance setup for Google
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
# from flask_dance.consumer import oauth_authorized, oauth_error # Signals are handled in auth_routes.py

# Create Google OAuth blueprint
# Note: client_id and client_secret are fetched from app.config,
# which should be populated from environment variables.
google_bp = make_google_blueprint(
    client_id=app.config.get("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=app.config.get("GOOGLE_OAUTH_CLIENT_SECRET"),
    scope=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
    # Use the OAuth model for storage. current_user is used to associate the token with the logged-in user.
    # user_required=False means it can operate even if no user is logged in (e.g., during initial OAuth dance).
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user, user_required=False),
    # redirect_url is optional if you want to override the default /google/authorized
    # redirect_to="auth_bp.profile" # Redirect after successful OAuth, handled by @oauth_authorized signal now
)
# Flask-Dance will automatically use current_app.secret_key for session protection.

# Import and register blueprints
from auth_routes import auth_bp
app.register_blueprint(google_bp, url_prefix="/login") # Flask-Dance blueprint for Google OAuth flow
app.register_blueprint(auth_bp) # Our custom auth routes (login, logout, profile)

# Set the login view for Flask-Login after blueprints are registered
login_manager.login_view = "auth_bp.login"


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback."""
    # user_id is typically the primary key of the User model, stored in the session
    return User.query.get(int(user_id))

# --- App Data (existing, might be refactored or removed if notes app takes over) ---
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
