from app import db # Import db instance from app.py
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin # Import the mixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True) # Google's unique ID for the user
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=True)
    profile_pic_url = db.Column(db.String(512), nullable=True)
    # Add other fields as needed, e.g., created_at, last_login

    # Relationship to OAuth model (for Flask-Dance token storage)
    # The 'oauth_google' backref can be used to access the token from the User object if needed.
    # oauth = db.relationship("OAuth", backref="user", lazy="joined") # Example if only one OAuth provider
                                                                # For multiple providers, this needs care.
                                                                # Flask-Dance's SQLAlchemyStorage handles this linkage.

    # Relationships (e.g., to Notes) will be added later
    # notes = db.relationship('Note', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.email}>'


# OAuth model for Flask-Dance SQLAlchemyStorage
# This model will store the OAuth tokens.
class OAuth(OAuthConsumerMixin, db.Model):
    # __tablename__ = "flask_dance_oauth" # Default table name if not specified
    # provider is already a column in OAuthConsumerMixin
    # created_at is already a column in OAuthConsumerMixin
    # token is already a column in OAuthConsumerMixin (JSON type)

    # Link to the User model
    # user_id is the foreign key to your User model's primary key.
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    # user relationship is automatically created by OAuthConsumerMixin if User model is passed to storage.
    # However, explicitly defining it can sometimes be clearer or necessary.
    user = db.relationship(User, backref=db.backref("oauth_credentials", lazy='dynamic'))

    # Flask-Login integration:
    # UserMixin provides is_authenticated, is_active, is_anonymous, get_id()
    # We just need to make sure our id field is compatible (which it is).
    # The get_id() method from UserMixin will return self.id as a string.
    # If your primary key was not 'id', you'd override get_id().

    # Example of how you might query:
    # @staticmethod
    # def find_by_email(email):
    #     return User.query.filter_by(email=email).first()

    # @staticmethod
    # def find_by_google_id(google_id):
    #     return User.query.filter_by(google_id=google_id).first()

    # @staticmethod
    # def create_or_update_from_oauth(oauth_user_info):
    #     user = User.find_by_google_id(oauth_user_info['sub']) # 'sub' is standard for subject/user ID
    #     if user:
    #         # Update if necessary
    #         user.email = oauth_user_info.get('email')
    #         user.name = oauth_user_info.get('name')
    #         user.profile_pic_url = oauth_user_info.get('picture')
    #     else:
    #         # Create new user
    #         user = User(
    #             google_id=oauth_user_info['sub'],
    #             email=oauth_user_info.get('email'),
    #             name=oauth_user_info.get('name'),
    #             profile_pic_url = oauth_user_info.get('picture')
    #         )
    #         db.session.add(user)
    #     db.session.commit()
    #     return user

# You can add other models here later, like Note, Tag, etc.
# from datetime import datetime
# class Note(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#
#     def __repr__(self):
#         return f'<Note {self.title}>'
