from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin  # type: ignore

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)
    image_url = db.Column(db.String(255), default='default.jpg')
    bio = db.Column(db.String(255), default='No bio')

    # Relationships
    recipes = db.relationship('Recipe', backref='user', lazy=True)

    # SerializerMixin configuration
    serialize_only = ('id', 'username', 'image_url', 'bio')

    @hybrid_property
    def password(self):
        raise AttributeError("Password hash is not accessible.")

    @password.setter
    def password(self, password):
        """Hash the password before storing it."""
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check if the given password matches the stored hash."""
        return bcrypt.check_password_hash(self._password_hash, password)


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    instructions = db.Column(db.String(255), nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # SerializerMixin configuration
    serialize_only = ('id', 'title', 'instructions', 'minutes_to_complete', 'user_id')

    @validates('title')
    def validate_title(self, key, title):
        """Validate that the title is not empty."""
        if not title:
            raise ValueError("Title cannot be empty.")
        return title

    @validates('instructions')
    def validate_instructions(self, key, instructions):
        """Validate that instructions are at least 50 characters long."""
        if len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return instructions

    @validates('minutes_to_complete')
    def validate_minutes_to_complete(self, key, minutes):
        """Validate that minutes to complete is a positive integer."""
        if minutes <= 0:
            raise ValueError("Minutes to complete must be a positive integer.")
        return minutes
