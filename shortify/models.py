"""ORM models for shortify
"""
from datetime import datetime as dt
from flask import redirect

from flask_login import UserMixin
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, login_manager


class UrlMap(db.Model):
    """Associates an original URL with a short one

    Attributes:
    id: Primary key
    original: Original URL
    short: Short URL alias
    timestamp: Timestamp. Defaults to utcnow.
    """

    id = db.Column(db.Integer(), primary_key=True)
    original = db.Column(db.Text(), nullable=False, index=True)
    short = db.Column(db.String(16), nullable=False, unique=True)
    timestamp = db.Column(db.DateTime(), default=dt.utcnow)
    hit_count = db.Column(db.Integer, default=0)
    expiration_date = db.Column(db.DateTime, nullable=True)
    suspended = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def increment_hit_count(self):
        self.hit_count += 1
        return self.save()

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    def is_owned_by(self, user):
        return self.user_id == user.id
    

class User(UserMixin, db.Model):
    """User model

    Attributes:
    id: Primary key
    first_name: User's first name
    last_name: User's last name
    email: User's email
    password: User's password
    timestamp: Timestamp. Defaults to utcnow.
    is_verified: Is user verified. Defaults to False.
    urls: Relationship to UrlMap

    """

    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(), nullable=True)
    last_name = db.Column(db.String(), nullable=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    timestamp = db.Column(db.DateTime(), default=dt.utcnow)
    is_verified = db.Column(db.Boolean(), default=False)
    urls = db.relationship("UrlMap", backref="user")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
        except IntegrityError:
            return False
        return True

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def __repr__(self):
        return f"<User {self.email}>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    return redirect("login")
