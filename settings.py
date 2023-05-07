import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", default="sqlite:///db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", default="lambada")
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 465
    MAIL_USERNAME = "mavhungutrezzy@gmail.com"
    MAIL_PASSWORD = os.getenv("GOOGLE_MAIL_PASSWORD")
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_DEFAULT_SENDER = "mavhungutrezzy@gmail.com"
