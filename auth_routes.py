from flask import Blueprint, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized, oauth_error
from sqlalchemy.orm.exc import NoResultFound
from app import db # Assuming db is initialized in app.py
from models import User # Assuming User model is in models.py

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

# We will register this blueprint with Flask-Dance later in app.py
# google_bp = make_google_blueprint(
#     client_id=current_app.config.get("GOOGLE_OAUTH_CLIENT_ID"),
#     client_secret=current_app.config.get("GOOGLE_OAUTH_CLIENT_SECRET"),
#     scope=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
#     redirect_url="/auth/login/google/authorized" # or use url_for
# )
# Note: The actual blueprint registration will be in app.py to handle app context for config.

@oauth_authorized.connect
def logged_in(blueprint, token):
    """
    This function is called when the user has successfully authenticated with Google.
    We can get the user's info and create/update them in our database.
    """
    if not token:
        flash("Failed to log in.", category="error")
        return redirect(url_for("index")) # Or a specific login failed page

    # Get user info from Google
    # The 'google' object here is the proxy to the Google blueprint provided by Flask-Dance
    resp = blueprint.session.get("/oauth2/v3/userinfo")
    if not resp.ok:
        msg = "Failed to fetch user info from Google."
        flash(msg, category="error")
        return redirect(url_for("index"))

    user_info = resp.json()
    google_user_id = str(user_info["sub"]) # 'sub' is the standard subject identifier
    email = user_info.get("email")
    name = user_info.get("name")
    profile_pic = user_info.get("picture")

    if not email:
        flash("Email not provided by Google. Cannot log in.", category="error")
        return redirect(url_for("index")) # Or a more specific error page

    # Find or create the user in our database
    user = User.query.filter_by(google_id=google_user_id).one_or_none()

    if user is None: # User not found by google_id, try by email just in case
        user = User.query.filter_by(email=email).one_or_none()
        if user: # User found by email, link google_id
            user.google_id = google_user_id
        else: # New user
            user = User(google_id=google_user_id, email=email)

    # Update user details
    user.name = name
    user.profile_pic_url = profile_pic

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Database error during login: {e}")
        flash("An error occurred while trying to log you in. Please try again.", category="error")
        return redirect(url_for("index"))

    login_user(user)
    flash("Successfully logged in with Google!", "success")
    return redirect(url_for("index")) # Or redirect to a user profile page


@oauth_error.connect
def google_error(blueprint, error, error_description=None, error_uri=None):
    """Handles errors during OAuth."""
    msg = (
        "OAuth error from {name}! "
        "error={error} description={description} uri={uri}"
    ).format(
        name=blueprint.name,
        error=error,
        description=error_description,
        uri=error_uri,
    )
    flash(msg, category="error")
    current_app.logger.error(msg)
    return redirect(url_for("index")) # Or a more specific error page


@auth_bp.route('/login')
def login():
    """Redirects to Google login."""
    # This route will be the one users click to "Login with Google"
    # It should redirect to the Flask-Dance Google blueprint's login route
    # The Google blueprint will be named 'google' by default with make_google_blueprint
    if not google.authorized: # google proxy object from Flask-Dance
        return redirect(url_for("google.login")) # 'google.login' is the default endpoint for the google_bp

    # If already authorized (e.g., session exists), redirect to profile or home
    flash("You are already logged in.", "info")
    return redirect(url_for('index'))


@auth_bp.route("/logout")
@login_required
def logout():
    """Logs the user out."""
    # For Flask-Dance, clearing the token is important if stored in session.
    # However, Flask-Login's logout_user handles the session part for our app's user.
    # If Flask-Dance stores its token in the session (default), it might need explicit clearing
    # depending on how `make_google_blueprint` storage is configured.
    # Often, `logout_user()` is enough if the blueprint doesn't aggressively re-authenticate.

    # blueprint_name = current_app.blueprints['google'].name # or just 'google'
    # token = current_app.blueprints['google'].token
    # if token:
    #     # This part is a bit more involved if you need to revoke the token with Google
    #     # For now, just logging out locally.
    #     pass

    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


# Example of a protected route
@auth_bp.route("/profile")
@login_required
def profile():
    # This is a simple protected route.
    # current_user is available from Flask-Login
    return f"Hello, {current_user.name}! Your email is {current_user.email}. <a href='{url_for('auth_bp.logout')}'>Logout</a>"

# We need to register this auth_bp and the google_bp in app.py
# The google_bp will be created using make_google_blueprint in app.py
# because it needs access to app.config for client_id and client_secret.
