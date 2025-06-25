import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
# This is primarily for local development.
# In production (e.g., on Render), environment variables should be set directly.
load_dotenv()

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess' # Default for safety
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google OAuth credentials
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')

    # Define the scope for Google OAuth
    # 'openid' and 'email' are common for basic user info
    # 'profile' gives access to the user's public profile information
    OAUTHLIB_INSECURE_TRANSPORT = os.environ.get('OAUTHLIB_INSECURE_TRANSPORT', '0') == '1' # Allow http for local dev if set

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///dev.db' # Default to SQLite for easy local dev if DATABASE_URL not set
    # For local development, you might want to allow insecure transport for OAuthlib
    # OAUTHLIB_INSECURE_TRANSPORT = '1' # Handled by base Config now

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # Ensure OAUTHLIB_INSECURE_TRANSPORT is False in production
    OAUTHLIB_INSECURE_TRANSPORT = False


# Determine which config to use based on FLASK_ENV or a default
# FLASK_ENV is not standard, FLASK_DEBUG is more common, or a custom APP_ENV
# For simplicity, we can default to DevelopmentConfig if FLASK_ENV is not 'production'
# However, Render typically sets NODE_ENV, which might not be relevant here.
# A common pattern is to use a custom env var like APP_SETTINGS.
# For now, let's keep it simple and assume direct env var usage in app.py for selection.

config_by_name = dict(
    development=DevelopmentConfig,
    production=ProductionConfig,
    default=DevelopmentConfig
)

# Helper function to load configuration based on environment variable
def load_app_config():
    env = os.getenv('FLASK_ENV', 'development') # Default to development
    return config_by_name.get(env, DevelopmentConfig)
