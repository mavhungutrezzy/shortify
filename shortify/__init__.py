from flask import Flask
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from settings import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
jwt = JWTManager(app)
mail = Mail(app)


from . import api_views, error_handlers, views

if app.env == "production":
    db.create_all()
